# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
import boto3
import botocore
import random
import string
import datetime
import rsa


def random_string(length=10):
    letters = string.digits + string.ascii_letters
    return ''.join(random.choice(letters) for x in range(length))


PRESETS = {
    '1080p': '1351620000001-000001',
    '720p': '1351620000001-000010',
    '480p': '1351620000001-000020',
    '360p': '1351620000001-000040',
}


class CourseConfig(models.Model):
    _inherit = "res.company"

    # AWS Access
    aws_access_key = fields.Char(string="AWS Access Key")
    aws_secret_key = fields.Char(string="AWS Secret Key")
    aws_region = fields.Char(string="AWS Region", default="us-east-1")

    # AWS Transcoder
    transcoder_pipeline_id = fields.Char(string="AWS Transcoder Pipeline ID")
    transcoder_pipeline_created = fields.Boolean(default=False)

    # AWS S3
    s3_bucket_input = fields.Char(string="S3 Bucket>Original Videos")
    s3_bucket_output = fields.Char(string="S3 Bucket>Formatted Videos")

    # Cloufront URL
    cloudfront_url = fields.Char(string="ClouFront URL")

    # URL Sign
    aws_signer_key_id = fields.Char(string="AWS Signer Key ID")
    aws_signer_private_key = fields.Text(string="AWS Signer Private Key")

    # Relationships
    course_ids = fields.One2many("efs_cm.course", "company_id", string="Mensajes enviados")

    def get_aws_client(self, service):
        if self.aws_access_key is None or self.aws_secret_key is None:
            raise exceptions.UserError("Configure Access Key and Access Secret")

        return boto3.client(service,
                            aws_access_key_id=self.aws_access_key,
                            aws_secret_access_key=self.aws_secret_key,
                            region_name=self.aws_region)

    def action_complete_buckets(self):
        if self.transcoder_pipeline_id is None:
            raise exceptions.UserError("Ingrese pipeline id.")

        client = self.get_aws_client('elastictranscoder')

        self.transcoder_pipeline_created = False
        try:
            pipe = client.read_pipeline(Id=self.transcoder_pipeline_id)
            pipe = pipe['Pipeline']

            self.s3_bucket_input = pipe['InputBucket']
            self.s3_bucket_output = pipe['ContentConfig']['Bucket']
        except botocore.exceptions.ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == "ResourceNotFoundException":
                raise exceptions.UserError("Pipeline not found")
            elif error_code == "UnrecognizedClientException":
                raise exceptions.UserError("AWS User not tiene permisos en transcoder.")
            else:
                raise exceptions.UserError("Error desconocido: " + str(e))
        except botocore.exceptions.BotoCoreError as e:
            raise exceptions.UserError(str(e))
        except Exception as e:
            raise exceptions.UserError(str(e))
        self.transcoder_pipeline_created = True

    def action_test_config(self):
        if self.cloudfront_url is None:
            raise exceptions.UserError("Cloudfront URL no ingresado")

        if not self.transcoder_pipeline_created:
            raise exceptions.UserError("Pipeline not validated")

        client = self.get_aws_client("s3")
        try:
            # test read input bucket
            client.list_objects(
                Bucket=self.s3_bucket_input,
                MaxKeys=1
            )
            client.list_objects(
                Bucket=self.s3_bucket_output,
                MaxKeys=1
            )
        except botocore.exceptions.ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == "InvalidBucketName":
                raise exceptions.UserError("Bucket not found.")
            elif error_code == "AccessDenied":
                raise exceptions.UserError("AWS User not tiene permisos en los buckets.")
            else:
                raise exceptions.UserError("Error desconocido: " + str(e))
        except Exception as e:
            raise exceptions.UserError(str(e))

    def rsa_signer(self, message):
        if self.aws_signer_private_key is None:
            raise exceptions.UserError("Signer Private Key not found.")
        return rsa.sign(message, rsa.PrivateKey.load_pkcs1(self.aws_signer_private_key.encode("utf8")), 'SHA-1')

    def get_signer(self):
        if not self.aws_signer_key_id or not self.aws_signer_private_key:
            raise exceptions.UserError("Signer Key ID not found.")
        return botocore.signers.CloudFrontSigner(self.aws_signer_key_id, self.rsa_signer)

    def sign_url(self, url, valid_time=1800, ipaddress=None):
        cf_signer = self.get_signer()
        now = datetime.datetime.utcnow() + datetime.timedelta(0, valid_time)
        policy = cf_signer.build_policy(url.split("?")[0], now, ip_address=ipaddress)
        return cf_signer.generate_presigned_url(url, policy=policy)

    def sign_s3_file(self, s3_file, **kwargs):
        url = self.cloudfront_url + s3_file
        return self.sign_url(url, **kwargs)


class Course(models.Model):
    _name = 'efs_cm.course'

    name = fields.Char(string="Nombre", required=True)
    description = fields.Text(string="Descripcion")

    company_id = fields.Many2one("res.company", string="Company", required=True)
    course_ids = fields.One2many("efs_cm.section", "course_id", string="Secciones")


class CourseSection(models.Model):
    _name = "efs_cm.section"
    name = fields.Char(string="Nombre", required=True)
    title = fields.Char(string="Titulo", required=True)

    course_id = fields.Many2one("efs_cm.course", string="Curso", required=True, ondelete="cascade")
    video_ids = fields.One2many("efs_cm.video", "section_id", string="Videos")


class CourseVideo(models.Model):
    _name = "efs_cm.video"
    name = fields.Char(string="Nombre")
    description = fields.Text(string="Description")

    s3_bucket_path = fields.Char(string="S3 File")
    autogenerated_code = fields.Char("Codigo Autogenerado")

    section_id = fields.Many2one("efs_cm.section", string="Seccion", required=True, ondelete="cascade")
    formats = fields.One2many("efs_cm.video_format", "video_id", string="Formats")

    def get_company(self):
        return self.section_id.course_id.company_id

    def action_check_video_existence(self):
        company = self.get_company()

        s3 = company.get_aws_client("s3")
        try:
            resp = s3.get_object(Bucket=company.s3_bucket_input, Key=self.s3_bucket_path)
        except botocore.exceptions.ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == "NoSuchKey":
                raise exceptions.UserError("El archivo no existe en el bucket: " + company.s3_bucket_input)
            else:
                raise exceptions.UserError("Error desconocido:\n" + str(e))
        except Exception as e:
            raise exceptions.UserError(str(e))

        if not self.autogenerated_code:
            self.autogenerated_code = random_string()

    def action_generate_formats(self):
        if len(self.formats) > 0:
            raise exceptions.UserError("Videos ya generados")

        company = self.get_company()
        transcoder = company.get_aws_client("elastictranscoder")

        outputs = []
        for size, preset_id in PRESETS.items():
            s3_file = self.autogenerated_code + "-" + size + ".mp4"
            outputs.append({
                'Key': s3_file,
                'Rotate': "0",
                'PresetId': preset_id,
            })
        transcoder.create_job(
            PipelineId=company.transcoder_pipeline_id,
            Input={
                'Key': self.s3_bucket_path,
                'FrameRate': 'auto',
                'Resolution': 'auto',
                'AspectRatio': 'auto',
                'Interlaced': 'auto',
                'Container': 'auto',
            },
            Outputs=outputs
        )
        for size, preset_id in PRESETS.items():
            s3_file = self.autogenerated_code + "-" + size + ".mp4"
            self.env['efs_cm.video_format'].create({
                's3_file': s3_file,
                'size': size,
                "video_id": self.id
            })

    def action_remove_formats(self):
        if len(self.formats) < 1:
            return
        company = self.get_company()
        s3 = company.get_aws_client("s3")

        for format in self.formats:
            s3.delete_object(Bucket=company.s3_bucket_output, Key=format.s3_file)
            format.unlink()

    def get_formats_signed_urls(self, **kwargs):
        ans = []
        for format in self.formats:
            ans.append({
                "size": format.size,
                "url": format.get_signed_url(**kwargs)
            })
        return ans


class CourseVideoFormats(models.Model):
    _name = "efs_cm.video_format"

    s3_file = fields.Char(string="S3 File")
    size = fields.Char(string="Size")

    video_id = fields.Many2one("efs_cm.video", string="Video", required=True, ondelete="cascade")

    def get_signed_url(self, **kwargs):
        company = self.video_id.get_company()
        return company.sign_s3_file(self.s3_file, **kwargs)

    def action_test_singed_url(self):
        if self.s3_file:
            raise exceptions.UserError(self.get_signed_url())
