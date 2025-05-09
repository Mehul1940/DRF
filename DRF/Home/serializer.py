from rest_framework import serializers 
from .models import Person , Color 
from django.contrib.auth.models import User


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email =serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):

        if data['username']:
            if User.objects.filter(username = data['username']).exists():
                raise serializers.ValidationError('username is taken')
            
        if data['email']:
            if User.objects.filter(email = data['email']).exists():
                raise serializers.ValidationError('email is taken')
        return data
    
    def create(self , validate_data):
        user = User.objects.create(username = validate_data['username'] , email = validate_data['email'])
        user.set_password(validate_data['password'])
        user.save()
        return validate_data
        

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['color_name']


class PeopleSerializer(serializers.ModelSerializer):
    # color = ColorSerializer()
    # color_info = serializers.SerializerMethodField()

    class Meta:
        model = Person
        # exclude = ['name','age']
        fields = '__all__'
        # depth = 1

    def get_color_info(self, obj):
        color_obj = Color.objects.get(id = obj.color_id)

        return {'color_name ': color_obj.color_name , 'hex_code' : '#000'}

    def validate(self, data):

        special_character = "!@#$%^&*()-+?=,<>/"
        if any(c in special_character for c in data['name']):
            raise serializers.ValidationError('name cannot contain special character')
        
        if data['age'] < 18:
            raise serializers.ValidationError('age should be greater than 18')
        return data
    
class SendMailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    subject = serializers.CharField(max_length=255)
    message = serializers.CharField()