from rest_framework import serializers
from users.models import Parent
from .user import UserDetailSerializer

class ParentSerializer(serializers.ModelSerializer):
    user_details = UserDetailSerializer(source='user', read_only=True)
    
    class Meta:
        model = Parent
        fields = ['id', 'user', 'user_details', 'parent_id', 'occupation', 'relationship_to_student']
        read_only_fields = ['id']

