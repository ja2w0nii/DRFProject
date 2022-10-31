from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.generics import get_object_or_404
from users.models import User

from users.serializers import UserSerializer, CustomTokenObtainPairSerializer, UserProfileSerializer


class UserView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"회원가입 완료!"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message":f"${serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        

class FollowView(APIView):
    def post(self, request, user_id):
        you = get_object_or_404(User, id=user_id)
        me = request.user
        if me in you.followers.all():
            you.followers.remove(me)
            return Response("unfollow 했습니다.", status=status.HTTP_200_OK)
        else:
            you.followers.add(me)
            return Response("follow 했습니다.", status=status.HTTP_200_OK)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class mockView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        #request.user의 정보를 조회 및 변경 할 수 있다. 원래는 post 요청으로 해야함.
        print(request.user)
        user = request.user
        user.is_admin = True
        user.save()
        return Response("get 요청")

class ProfileView(APIView):
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)