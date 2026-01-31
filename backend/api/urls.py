from django.urls import path
from .views import AnalyzeView, HistoryView, DownloadPDFView

urlpatterns = [
    path('analyze/', AnalyzeView.as_view()),
    path('history/', HistoryView.as_view()),
    path('report/', DownloadPDFView.as_view()),
]