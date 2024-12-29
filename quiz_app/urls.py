from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import signup



app_name = 'quiz_app'  # Questo è opzionale, ma utile per namespace

urlpatterns = [
    path('', views.home, name='home'),
    path('start/', views.start_quiz, name='start_quiz'),
    path('start/<str:quiz_type>/', views.start_quiz, name='start_quiz'),
    path('question/<int:quiz_session_id>/<int:question_number>/', views.question, name='question'),
    path('load_next_question/<int:quiz_session_id>/<int:question_number>/', views.load_next_question, name='load_next_question'),
    path('preload_next_question/<int:quiz_session_id>/<int:question_number>/', views.preload_next_question, name='preload_next_question'),
    path('results/<int:quiz_session_id>/', views.quiz_results, name='quiz_results'),
    path('performance_trend/<int:days>/', views.get_performance_trend_for_user, name='performance_trend'),
    path('performance_data/<int:days>/', views.performance_data, name='performance_data'),
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('load_next_question/<int:quiz_session_id>/<int:question_number>/', views.load_next_question, name='load_next_question'),
    path('toggle_follow/<str:username>/', views.toggle_follow, name='toggle_follow'),
    path('search/', views.user_search, name='user_search'),
    path('statistics/', views.statistics_view, name='statistics'),
    path('signup/', signup, name='signup'),
    #path('confirm/<uidb64>/<token>/', views.confirm_email, name='confirm_email'),
    path('followers/<str:username>/', views.get_followers, name='get_followers'),
    path('following/<str:username>/', views.get_following, name='get_following'),
    path('statistics/download/difficult_species/', views.download_difficult_species, name='download_difficult_species'),
    path('statistics/download/user_performance/', views.download_user_performance, name='download_user_performance'),
    path('statistics/download/common_errors/', views.download_common_errors, name='download_common_errors'),
    path('statistics/download/all/', views.download_all_statistics, name='download_all_statistics'),
    path('debug_statistics/', views.debug_statistics, name='debug_statistics'),
    path('api/notification-count/', views.notification_count, name='notification_count'),
    path('notifications/', views.notifications, name='notifications'),
    path('achievements/', views.all_achievements, name='all_achievements'),
    path('api/notifications/', views.get_notifications, name='get_notifications'),
    path('notification/<int:notification_id>/mark-as-read/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('api/species-suggestions/', views.species_suggestions, name='species_suggestions'),
    path('update_avatar/', views.update_avatar, name='update_avatar'),
    path('random_users/', views.random_users, name='random_users'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('confirm/<uidb64>/<token>/', views.confirm_email, name='confirm_email'),
]