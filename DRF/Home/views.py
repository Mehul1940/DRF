from rest_framework.decorators import api_view , action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Person
from Home.serializer import *
from django.core.mail import send_mail
from rest_framework import viewsets 
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import  IsAuthenticated 
from rest_framework.authentication import TokenAuthentication
from django.core.paginator import Paginator ,  EmptyPage, PageNotAnInteger



class LoginAPI(APIView):

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'status': False, 'message': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(username=username, password=password)

        if not user:
            return Response(
                {'status': False, 'message': 'Invalid username or password'},
                status=status.HTTP_400_BAD_REQUEST
            )

        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {'status': True, 'message': 'User logged in', 'token': str(token)},
            status=status.HTTP_200_OK
        )

    
class RegisterAPI(APIView):
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {'status': False, 'message': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = serializer.save()

        return Response(
            {
                'status': True,
                'message': 'User created successfully',
                'user_id': user.id,
                'username': user.username,
                'password': user.password
            },
            status=status.HTTP_201_CREATED
        )


@api_view(['GET', 'POST', 'PUT'])
def index(request):
    courses = {
        "course_name": "Python",
        "learn": ['Flask', 'Django', 'Tornado', 'FastApi'],
        'course_provider': "Scaler"
    }

    if request.method == 'GET':
        search_query = request.GET.get('search')
        print(f"[GET] Search Query: {search_query}")
        return Response(courses, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        data = request.data
        age = data.get('age')
        print(f"[POST] Received age: {age}")
        return Response(courses, status=status.HTTP_201_CREATED)

    elif request.method == 'PUT':
        print("[PUT] Request received.")
        return Response(courses, status=status.HTTP_200_OK)
    
@api_view(['POST'])
def login(request):
    data = request.data
    serializer = LoginSerializer(data = data)
    
    if serializer.is_valid():
        data = serializer.data
        print(data)
        return Response({'message': 'success'})

    return Response(serializer.errors)

class PersonAPI(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        try:
            # Get queryset with consistent ordering
            people = Person.objects.all().order_by('id')
            
            # Get pagination parameters from request
            page = request.GET.get('page', 1)
            page_size = int(request.GET.get('page_size', 3))
            
            # Validate page_size
            if page_size > 100:
                return Response(
                    {'error': 'Maximum page size is 100'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            paginator = Paginator(people, page_size)

            try:
                paged_people = paginator.page(page)
            except PageNotAnInteger:
                paged_people = paginator.page(1)
            except EmptyPage:
                return Response(
                    {
                        'error': f'Page out of range. Valid pages: 1-{paginator.num_pages}'
                    }, 
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = PeopleSerializer(paged_people, many=True)
            
            return Response({
                'total_records': paginator.count,
                'total_pages': paginator.num_pages,
                'current_page': paged_people.number,
                'next_page': paged_people.next_page_number() if paged_people.has_next() else None,
                'previous_page': paged_people.previous_page_number() if paged_people.has_previous() else None,
                'results': serializer.data
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response(
                {'error': 'Invalid page parameter'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        serializer = PeopleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        person_id = request.data.get('id')
        if not person_id:
            return Response({'error': 'ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            instance = Person.objects.get(id=person_id)
        except Person.DoesNotExist:
            return Response({'error': 'Person not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PeopleSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        person_id = request.data.get('id')
        if not person_id:
            return Response({'error': 'ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            instance = Person.objects.get(id=person_id)
        except Person.DoesNotExist:
            return Response({'error': 'Person not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PeopleSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        person_id = request.data.get('id')
        if not person_id:
            return Response({'error': 'ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            instance = Person.objects.get(id=person_id)
            instance.delete()
            return Response({'message': 'Person deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Person.DoesNotExist:
            return Response({'error': 'Person not found'}, status=status.HTTP_404_NOT_FOUND)

class peopleViewSet(viewsets.ModelViewSet):
    serializer_class = PeopleSerializer
    queryset = Person.objects.all()

    def list(self, request, *args, **kwargs):
        search = request.GET.get('search')
        queryset = self.queryset
        if search:
            queryset = queryset.filter(name__startswith = search)
        serializer = PeopleSerializer(queryset , many = True)
        return Response({'status':200 , 'data': serializer.data})
    
    @action(detail=False, methods=['post'])
    def send_mail_to_person(self, request):
        serializer = SendMailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            subject = serializer.validated_data['subject']
            message = serializer.validated_data['message']

            # Send the email
            send_mail(
                subject,
                message,
                'bokdemehul870@gmail.com',  
                [email],
                fail_silently=False,
            )

            return Response({'status': True, 'message': 'Email sent successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


