import json
from PIL import Image
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response 
import rest_framework.permissions as permissions
from rest_framework.decorators import action 
from rest_framework.parsers import MultiPartParser, JSONParser
from django.core.files.uploadedfile import UploadedFile

from instagram_app.models import Profile
from instagram_app.serializers import ProfileSerializer 

class ProfilesViewSet(ViewSet): 
    parser_classes = [MultiPartParser, JSONParser]
    def get_permissions(self): 
        if self.action in ["retrieve", "retrieve_follows"]: 
            return [] 
        else: 
            return [permissions.IsAuthenticated()] 

    def retrieve(self, request, pk=None): 
        profile = get_object_or_404(Profile, pk=pk)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=200)

    @action(detail=False, methods=["GET", "PUT"], url_name="me") 
    def me(self, request): 
        if request.method == "GET": 
            return self._retrieve_me(request)
        elif request.method == "PUT": 
            return self._update_me(request)

    def _retrieve_me(self, request): 
        profile = request.user.profile 
        data = ProfileSerializer(profile).data 
        data['followsProfiles'] = ProfileSerializer(profile.follows, many=True).data
        return Response(data, status=200)
    def _update_me(self, request): 
        profile = request.user.profile
        if request.data.get('about'): 
            profile.about = request.data['about']
            profile.save() 
        if request.data.get('avatar'): 
            image_file = request.data['avatar'] 
            print(image_file) 
            print(type(image_file));
            if not issubclass(type(image_file), UploadedFile):
                return Response(status=400)
            # check that provided file is truly a valid image (not some .js file or something like that)
            try: 
                im = Image.open(image_file)
                im.verify() 
            except: 
                return Response({
                    'detail': 'What you uploaded is not a valid image.'
                }, status=400)
            
            profile.update_avatar(image_file)
        return self._retrieve_me(request)
    
    @action(detail=True, methods=["GET"], url_name="follows")
    def retrieve_follows(self, request, pk=None): 
        target_user = get_object_or_404(Profile, pk=pk)
        follows = {
            'profiles': ProfileSerializer(target_user.follows.all(), many=True).data,
        }
        return Response(follows, status=200)
    
    @action(detail=True, methods=["POST"], url_name="toggle-follow")
    def toggle_follow(self, request, pk=None): 
        target_user = get_object_or_404(Profile, pk=pk) 
        acting_user = request.user.profile
        if target_user.followers.filter(pk=acting_user.pk).exists(): 
            target_user.followers.remove(acting_user) 
        else: 
            target_user.followers.add(acting_user)
        return Response({}, status=200)
