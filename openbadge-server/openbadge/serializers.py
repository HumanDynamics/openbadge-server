from rest_framework import serializers
import time

from .models import Member, Project, Hub


class MemberSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())

    class Meta:
        model = Member
        fields = ('id', 'project', 'name', 'email', 'badge', 'last_seen_ts', 'last_audio_ts',
                  'last_audio_ts_fract', 'last_proximity_ts', 'last_voltage', 'key')
        read_only_fields = ('project', 'id', 'key', 'badge', 'name', 'email')

    def update(self, instance, validated_data):

        # if we have an older audio_ts, update it
        if validated_data.get('last_audio_ts') > instance.last_audio_ts:
            instance.last_audio_ts = validated_data.get('last_audio_ts',
                                                instance.last_audio_ts)
            instance.last_audio_ts_fract = validated_data.get('last_audio_ts_fract',
                                                instance.last_audio_ts_fract)

        # if we have an older proximity_ts, update it
        if validated_data.get('last_proximity_ts') > instance.last_proximity_ts:
            instance.last_proximity_ts = validated_data.get('last_proximity_ts', instance.last_proximity_ts)

        # if we have an older last_seen_ts, update it and voltage
        if validated_data.get('last_seen_ts') > instance.last_seen_ts:
            instance.last_seen_ts = validated_data.get('last_seen_ts', instance.last_seen_ts)
            instance.last_voltage = validated_data.get('last_voltage', instance.last_voltage)

        instance.save()
        return instance

class HubSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())

    class Meta:
        model = Hub
        fields = ('id', 'project', 'name', 'last_seen_ts',
                  'god', 'uuid', 'ip_address', 'key')
        read_only_fields = ('id', 'project', 'name',
                            'heartbeat', 'key', 'god', 'uuid')
