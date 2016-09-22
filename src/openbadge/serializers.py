from rest_framework import serializers

from .models import Member, Project


class MemberSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())

    class Meta:
        model = Member
        fields = ('id', 'project', 'name', 'email', 'badge', 'init_audio_ts', 'init_audio_ts_fract',
                  'init_proximity_ts', 'key',
                  )
        read_only_fields = ('project', 'id', 'key', 'badge', 'name', 'email')

    def update(self, instance, validated_data):

        if validated_data.get('init_audio_ts') < instance.init_audio_ts or \
                validated_data.get('init_audio_ts_fract') < instance.init_audio_ts_fract or \
                validated_data.get('init_proximity_ts') < instance.init_proximity_ts:

            raise serializers.ValidationError('Found newer init_audio_ts, init_audio_ts_fract, or init_proximity_ts '
                                               'in the existing Badge')

        instance.init_audio_ts = validated_data.get('init_audio_ts', instance.init_audio_ts)
        instance.init_audio_ts_fract = validated_data.get('init_audio_ts_fract', instance.init_audio_ts_fract)
        instance.init_proximity_ts = validated_data.get('init_proximity_ts', instance.init_proximity_ts)

        instance.save()

        return instance
