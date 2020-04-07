import json


from cic_network.cicn_users.serializers import (UserSerializer,
                                                UserRegistrationSerializer,
                                                ProfileSerializer,
                                                SocialNetworkSerializer)
from cic_network.cicn_users.models import User, SocialNetwork, Profile

from cic_network.mixins import DatatablesMixin

from django.contrib.auth.models import Permission, Group


from cic_network.cicn_courses.models import Teacher
from cic_network.cicn_courses.serializers import CohortSerializer
from cic_network.cicn_polls.serializers import FastPollSerializer, PollSerializer
from django.contrib.auth import authenticate, login, logout

# Vista base para crear las peticiones ajax
from django.views.generic import RedirectView
from django.http import HttpResponse

from  firebase_app.app  import lms_app


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
from rest_framework.views import APIView
from django.db.models import F  
# class RolePermission(BasePermission):
#     """
#     Global permission check for blacklisted IPs.
#     """
#     message = 'El usuario no tiene permisos.'
#     def has_permission(self, request, view):
#         ip_rol = request.user.rol
#         blacklisted = Blacklist.objects.filter(ip_addr=ip_addr).exists()
#         return not blacklisted

class IsUserProfileOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj == request.user

# class UserViewSet(, viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer


class SocialNetworkViewSet(viewsets.ModelViewSet):
    queryset = SocialNetwork.objects.all()
    serializer_class = SocialNetworkSerializer

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def fromProfile(self, request,  *args, **kwargs):
        profile = Profile.objects.get(pk=request.query_params['profile'])
        serlializer= self.get_serializer(data=profile.networks.all(), many=True)
        serlializer.is_valid()
        return Response(serlializer.data)
        
        

    # def create(self, request):
    #     # Validating our serializer from the UserRegistrationSerializer

    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     import pdb; pdb.set_trace()
    #     serializer.save()
    #     return Response(serialized.data, status=status.HTTP_201_CREATED)

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
    
    # def list(self, request,  *args, **kwargs):
    #     # import pdb; pdb.set_trace()
    #     return super(UserViewSet, self).list(request)

    # def get_permissions(self):
    #     if self.action == 'detail':
    #         permission_classes = [IsAuthenticated]
    #     else:
    #         permission_classes = [IsUserProfileOwner]
    #     return [permission() for permission in permission_classes]

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
        # Validating our serializer from the UserRegistrationSerializer
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        rol = serializer.validated_data['rol']
        # import pdb; pdb.set_trace()
        serializer.save()
        if int(rol) <= 1:
            Teacher.objects.create(user=serializer.instance)
            tp = serializer.instance.teacher_profile

        # import pdb; pdb.set_trace()


        # Everything's valid, so send it to the UserSerializer
        # model_serializer = UserSerializer(data=serializer.data)
        # model_serializer.is_valid(raise_exception=True)
        # model_serializer.save()

        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def user_search(self, request, pk=None):
        lookup = self.request.query_params.get('search', None)
        if lookup is None:
            return Response()

        qs=self.get_queryset()
        qs=qs.filter(first_name__icontains=lookup).union(
            qs.filter(last_name__icontains=lookup)).union(
            email__icontains=lookup)

        return  UserSerializer(qs,many=True)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def courses(self, request, pk=None):
        '''dcstring for '''
        user = self.get_object()
        part = user.participation

        courses = []
        for course in part.all():
            courses.append(course.cohort)

        context = self.get_serializer_context()
        serialized = CohortSerializer(courses, many=True,  context=context)
        return Response(serialized.data)

    # @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    # def courses(self, request, pk=None):
    #     '''dcstring for '''
    #     user = self.get_object()
    #     part = user.participation
    #
    #     courses = []
    #     for course in part.all():
    #         courses.append(course.cohort)
    #
    #     context = self.get_serializer_context()
    #     serialized = CohortSerializer(courses, many=True,  context=context)
    #     return Response(serialized.data)

    def my_function(x):
        return

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
            # for poll in serialized.data:
            #     user_esp_respondants = [resp['user'] for resp in poll['expected_respondants']]

            # is_expected=True if user.id in user_esp_respondants else False
            #
            # if is_expected:
            #     responded = True if user.id in [resp['user'] for resp in poll['respondants']] else False
            #     user_idx=user_esp_respondants.index(user.id)
            #     user_participation=poll['expected_respondants'][user_idx]
            #     poll['user_participation'] = user_participation
            #
            # else:
            #     poll['user_participation'] = None
            #     responded=False
            # poll['is_expected'] = is_expected
            # poll['responded'] = responded
            #
            # if is_expected and not responded:

        # serialized = FastPollSerializer(to_respond, many=True)
        return Response(to_respond)


    @action(detail=True, methods=['patch',], permission_classes=[IsAuthenticated])
    def profileImage(self, request, pk=None):
        '''docstring for profile_image'''
        # import pdb; pdb.set_trace()
        
        instance=self.get_object().profile
        serialized = ProfileSerializer(
            instance,
            data=request.data,
            partial=True)
        serialized.is_valid(raise_exception=True)
        serialized.save()
        return Response(serialized.data)

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

    @action(detail=True, methods=['patch',], permission_classes=[IsAuthenticated])
    def change_userrole(self, request, pk=None):
        if int(self.request.user.rol)>0:
            # import pdb;pdb.set_trace()
            return Response(data="{'message':'No cuenta con los permisos para realizar esta acción'}", status=200)

        new_rol=request.data.get('user_role',None)
        if new_rol is None:
            return Response(data="{'message':'Los datos son invalidos'}", status=400)
        user=self.get_object()
        user.rol=new_rol
        user.save()
        if new_rol == 0:
            u_group = Group.objects.get(name='Administrator')
        if new_rol == 1:
            u_group = Group.objects.get(name='Teacher')
        if new_rol == 2:
            u_group = Group.objects.get(name='Represetant')
        if new_rol == 3:
            u_group = Group.objects.get(name='Alumno')
        
        # import pdb; pdb.set_trace()
        if new_rol is not None:
            user.groups.set([u_group])
        return Response(data="{'message':'se ha cambiado el rol del usuario con exito'}", status=200)


def JSONResponse(message, url=None):
    return HttpResponse(
            json.dumps({"message": message, "url":url}),
            content_type="application/json")


@api_view(['POST'])
def register_user(request):
    serialized = UserRegistrationSerializer(data=request.data)
    serialized.is_valid(raise_exception=True)
    serialized.save()
    # login(request, serializ)
    return Response(serialized.data, status=status.HTTP_201_CREATED)




class AjaxLogout(RedirectView):
    """ Logout a traves de una peticiónm Ajax"""

    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponse(
            json.dumps({"message": "Sesion Cerrada"}),
            content_type="application/json")

class AjaxLogin(RedirectView):
    """ Login a traves de una peticiónm Ajax"""

    def get(self, request, *args, **kwargs):
        token = request.META.get('HTTP_FIREBASE')
        print('tokenAuth')
        if token:
            lms_app.verify_token(token)
        import pdb; pdb.set_trace()
        import pdb; pdb.set_trace()
        user = authenticate(
            email=request.POST.get('email'),
            password=request.POST.get('password')
            )

        if user is not None:
            if user.is_active:
                login(request, user)
                return JSONResponse("Exito")
            else:
                return JSONResponse("Usuario Inactivo o bloqueado")
        else:
            return JSONResponse("Combinación de usuario y contraseña incorrecto")

class Auth(APIView):

    def get(self, request,*args, **kwargs):
        """ Logout a traves de una petición Ajax"""
        # import pdb; pdb.set_trace()
        logout(request)
        return Response({"message": "Sesion Cerrada"}, status=202)

    def post(self, request, *args, **kwargs):
        """ Login a traves de una petición Ajax"""

        token = request.META.get('HTTP_FIREBASE')
        if token:
            decoded_token = lms_app.verify_token(token)
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
