from rest_framework import serializers


class AttachmentSerializer(serializers.Serializer):
    name = serializers.CharField()
    content_type = serializers.CharField()
    data = serializers.CharField()


class SendEmailSerializer(serializers.Serializer):
    from_email = serializers.EmailField()
    from_name = serializers.CharField()
    subject = serializers.CharField()
    template_id = serializers.IntegerField()
    recipients = serializers.ListSerializer(
        child=serializers.EmailField(), allow_empty=False
    )
    reply_to = serializers.ListSerializer(
        child=serializers.EmailField(required=True), allow_empty=True, required=False
    )
    variables = serializers.DictField(allow_empty=True, required=False)
    attachments = serializers.ListSerializer(
        child=AttachmentSerializer(), allow_empty=True, required=False
    )
