from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from elasticsearch import Elasticsearch

ELASTIC_PASSWORD = "+TQ3lG=S3jAfZb7RE59j"
es_client = Elasticsearch( "https://localhost:9200/",  basic_auth=("elastic", ELASTIC_PASSWORD), verify_certs=False,  ssl_show_warn=False )


class CountAllStudents(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        try:
            # Get the cd_etab parameter from the request
            cd_etab = request.GET.get('cd_etab')

            if not cd_etab:
                return JsonResponse({"error": "cd_etab parameter is required"}, status=400)

            # Construct the body with a filter for cd_etab
            body = {
                "size": 0,
                "query": {
                    "term": {
                        "cd_etab.keyword": cd_etab
                    }
                },
                "aggs": {
                    "total_students": {
                        "value_count": {"field": "id_eleve"}
                    },
                    "unique_classes": {
                        "cardinality": {"field": "id_classe.keyword"}
                    }
                }
            }

            response = es_client.search(index="data_middle*", body=body)
            
            def format_number(value):
                return f'{value / 1000:.1f}K' if value >= 1000 else str(value)
            
            results = {
                "total_students": format_number(response['aggregations']['total_students']['value']),
                "number_of_unique_classes": format_number(response['aggregations']['unique_classes']['value'])
            }
            return JsonResponse(results, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
