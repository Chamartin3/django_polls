from cic_network.cicn_courses import views
from cic_network.cicn_polls import views as poll_views

from rest_framework.routers import DefaultRouter

polls_api = DefaultRouter()

polls_api.register(r'polls', poll_views.PollViewSet)
polls_api.register(r'questions', poll_views.QuestionViewSet)


urlpatterns = polls_api.urls