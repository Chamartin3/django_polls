# Python
import json

# Django
from django.db.models import F  
from django.http import HttpResponse
from django.views.generic import RedirectView
from django.contrib.auth.models import Permission, Group
from django.contrib.auth import authenticate, login, logout

# Django Rest Framewirk 
from rest_framework import filters
from rest_framework import status, viewsets, serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.parsers import MultiPartParser,FormParser,JSONParser, FileUploadParser
from rest_framework.permissions import (IsAuthenticated,
                                        BasePermission,
                                        AllowAny,
                                        SAFE_METHODS,
                                        DjangoModelPermissions)

# Local
from rest_framework.views import APIView
from cic_network.cicn_users.models import User, Profile
from .cicn_users.serializers import (UserSerializer,
                                                UserRegistrationSerializer,
                                                ProfileSerializer,
                                                SocialNetworkSerializer)



class IsUserProfileOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj == request.user

class UserViewSet(DatatablesMixin,viewsets.ModelViewSet):
    queryset = User.objects.order_by(F('last_login').desc(nulls_last=True))
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['first_name', 'last_name', 'email', 'profile__nacionality']

    def get_queryset(self):
        cohortfilter = self.request.query_params.get('participation__cohort', None)
        if cohortfilter:
            self.queryset = self.queryset.filter(participation__cohort=cohortfilter)
        return super(UserViewSet, self).get_queryset()
    

    def partial_update(self, request, pk=None):
        user = self.get_object()
        self.check_object_permissions(self.request, user)
        response = super(UserViewSet, self).partial_update(request, pk)
        rol = response.data.get('rol',None)

        if rol == 0:
            u_group = Group.objects.get(name='Administrator')
        if rol == 1:
            u_group = Group.objects.get(name='Teacher')
        if rol == 2:
            u_group = Group.objects.get(name='Represetant')
        if rol == 3:
            u_group = Group.objects.get(name='Alumno')
        if rol is not None:
            user.groups.set([u_group])

        if int(rol) <= 1:
            Teacher.objects.get_or_create(user_id=response.data['id'])
        return response

    def create(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rol = serializer.validated_data['rol']
        serializer.save()
        if int(rol) <= 1:
            Teacher.objects.create(user=serializer.instance)
            tp = serializer.instance.teacher_profile
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def search(self, request, pk=None):
        lookup = self.request.query_params.get('search', None)
        if lookup is None:
            return Response()

        qs=self.get_queryset()
        qs=qs.filter(first_name__icontains=lookup).union(
            qs.filter(last_name__icontains=lookup)).union(
            email__icontains=lookup)
        return  UserSerializer(qs,many=True)


    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def polls_to_response(self, request, pk=None):
        '''dcstring for '''
        user = self.get_object()
        to_respond=[]
        participations=user.participation.all().prefetch_related('responses').select_related('cohort')
        for part in participations.iterator():

            # import pdb; pdb.set_trace()
            polls_responded=[r.poll for r in part.responses.all()]
            polls_to_respond=[FastPollSerializer(p).data for p in part.cohort.polls.all() if p not in  polls_responded]

            for p in polls_to_respond:
                p['user_participation']=part.id
                to_respond.append(p)
        return Response(to_respond)


    @action(detail=True, methods=['patch',], permission_classes=[IsAuthenticated])
    def changePassword(self, request, pk=None):
        data=request.data
        if not data.get('password') or not data.get('passwordconf'):
            raise serializers.ValidationError("{'message':'Ingresa una contraseña y confirmala.''")

        if data.get('password') != data.get('passwordconf'):
            raise serializers.ValidationError("{'message':'Las contraseñas no coinciden.'}")

        user=self.get_object()
        user.set_password(data.get('password'))
        user.save()
        return Response(data="{'message':'La contraseña se ha cambiado con exito'}", status=200)

class Auth(APIView):

    def get(self, request,*args, **kwargs):
        """ Logout a traves de una petición Ajax"""
        logout(request)
        return Response({"message": "Sesion Cerrada"}, status=202)
    def post(self, request, *args, **kwargs):
        """ Login a traves de una petición Ajax"""
        user = authenticate(
            email=request.data.get('email'),
            password=request.data.get('password')
        )
        if user is not None:
            if user.is_active:
                login(request, user)
                return Response({'message':"Exito"}, status=202)
            else:
                return Response({'message':"Este Usuario se encuentra inactivo o bloqueado, contacte a un adminitrador para mas información"}, status=401)
        else:
            return Response({'message':"Combinación de usuario y contraseña incorrecto"}, status=401)
