from rest_framework import serializers
import time

from .models import Member, Project, Hub, Beacon


class MemberSerializer(serializers.ModelSerializer):
    advertisment_project_id = serializers.ReadOnlyField(source='get_project_id')

    class Meta:
        model = Member
        fields = ('id', 'advertisment_project_id', 'name', 'email', 'badge', 'observed_id', 'active', 'comments','last_seen_ts', 'last_audio_ts',
                  'last_audio_ts_fract', 'last_proximity_ts', 'last_contacted_ts', 'last_unsync_ts', 'last_voltage', 'key')
        read_only_fields = ('id','advertisment_project_id', 'key')

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


        # if we have an older last_contacted_ts, update it
        if validated_data.get('last_contacted_ts') > instance.last_contacted_ts:
            instance.last_contacted_ts = validated_data.get('last_contacted_ts', instance.last_contacted_ts)

        if validated_data.get('last_unsync_ts') > instance.last_unsync_ts:
            instance.last_unsync_ts = validated_data.get('last_unsync_ts', instance.last_unsync_ts)

        instance.observed_id = validated_data.get('observed_id', instance.observed_id)

        instance.save()
        return instance



class BeaconSerializer(serializers.ModelSerializer):
    advertisment_project_id = serializers.ReadOnlyField(source='get_project_id')
    
    class Meta:
        model = Beacon
        fields = ('id', 'advertisment_project_id','name', 'badge', 'observed_id','active', 'comments',
         'last_seen_ts','last_voltage', 'key')
        read_only_fields = ('advertisment_project_id', 'id', 'key')

    def update(self, instance, validated_data):
        # if we have an older last_seen_ts, update it and voltage
        if validated_data.get('last_seen_ts') > instance.last_seen_ts:
            instance.last_seen_ts = validated_data.get('last_seen_ts', instance.last_seen_ts)
            instance.last_voltage = validated_data.get('last_voltage', instance.last_voltage)

        instance.observed_id = validated_data.get('observed_id', instance.observed_id)

        instance.save()
        return instance


class HubSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())

    class Meta:
        model = Hub
        fields = ('id', 'advertisment_project_id', 'name', 'last_seen_ts',
                  'god', 'uuid', 'ip_address', 'key')
        read_only_fields = ('id', 'advertisment_project_id', 'name',
                            'heartbeat', 'key', 'god', 'uuid')
