from rest_framework import serializers

from .models import Member, Project, Hub


class MemberSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())

    class Meta:
        model = Member
        fields = ('id', 'project', 'name', 'email', 'badge', 'last_seen_ts', 'last_audio_ts',
                  'last_audio_ts_fract', 'last_proximity_ts', 'last_voltage', 'key')
        read_only_fields = ('project', 'id', 'key', 'badge', 'name', 'email')

    def update(self, instance, validated_data):

        if validated_data.get('last_audio_ts') < instance.last_audio_ts or \
                validated_data.get('last_proximity_ts') < instance.last_proximity_ts:

            raise serializers.ValidationError('Found newer last_audio_ts, or last_proximity_ts '
                                               'in the existing Badge')

        instance.last_audio_ts = validated_data.get('last_audio_ts', instance.last_audio_ts)
        instance.last_audio_ts_fract = validated_data.get('last_audio_ts_fract', instance.last_audio_ts_fract)
        instance.last_proximity_ts = validated_data.get('last_proximity_ts', instance.last_proximity_ts)
        instance.last_voltage = validated_data.get('last_voltage', instance.last_voltage)

        instance.save()

        return instance

class HubSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())

    class Meta:
        model = Hub
        fields = ('id', 'project', 'name', 'heartbeat',
                  'god', 'uuid', 'ip_address', 'key')
        read_only_fields = ('id', 'project', 'name',
                            'heartbeat', 'key', 'god', 'uuid')
