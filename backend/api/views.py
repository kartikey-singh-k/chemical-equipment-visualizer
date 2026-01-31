import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .models import EquipmentBatch
from .serializers import EquipmentBatchSerializer
from django.http import HttpResponse
from reportlab.pdfgen import canvas

class AnalyzeView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 1. Read CSV using Pandas
            df = pd.read_csv(file_obj)
            
            # 2. Validation (Check if required columns exist)
            required_cols = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
            if not all(col in df.columns for col in required_cols):
                return Response({"error": f"CSV must contain: {required_cols}"}, status=400)

            # 3. Compute Analytics
            stats = {
                "total_count": len(df),
                "avg_pressure": round(df['Pressure'].mean(), 2),
                "avg_temp": round(df['Temperature'].mean(), 2),
                "avg_flow": round(df['Flowrate'].mean(), 2),
                "type_distribution": df['Type'].value_counts().to_dict()
            }

            # 4. Save to DB (Keep only last 5)
            EquipmentBatch.objects.create(filename=file_obj.name, summary_stats=stats)
            
            last_5_ids = EquipmentBatch.objects.order_by('-uploaded_at').values_list('id', flat=True)[:5]
            EquipmentBatch.objects.exclude(id__in=last_5_ids).delete()

            # 5. Return Data
            return Response({
                "stats": stats,
                "data": df.head(50).to_dict(orient='records') # Limit to 50 rows for display
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)

class HistoryView(APIView):
    def get(self, request):
        batches = EquipmentBatch.objects.order_by('-uploaded_at')
        serializer = EquipmentBatchSerializer(batches, many=True)
        return Response(serializer.data)

class DownloadPDFView(APIView):
    def post(self, request):
        # Generate simple PDF report on the fly
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="report.pdf"'
        
        data = request.data
        p = canvas.Canvas(response)
        p.drawString(100, 800, "Chemical Equipment Report")
        p.drawString(100, 780, "-" * 30)
        p.drawString(100, 760, f"Total Equipment: {data.get('total_count')}")
        p.drawString(100, 740, f"Avg Pressure: {data.get('avg_pressure')} bar")
        p.drawString(100, 720, f"Avg Temperature: {data.get('avg_temp')} C")
        p.showPage()
        p.save()
        return response