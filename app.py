import tornado.ioloop
import tornado.web
import os
import subprocess
import tempfile
import uuid
from pathlib import Path
from tornado.log import enable_pretty_logging
class Config:
    MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = {'.html', '.htm'}

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("upload.html")

class TailwindBuilder:
    def build_css(self, html_content):
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                unique_id = uuid.uuid4()
                html_filename = f"input_{unique_id}.html"
                css_filename = f"output_{unique_id}.css"

                html_path = temp_path / html_filename
                with open(html_path, "w") as f:
                    f.write(html_content)


                css_output_path = temp_path / css_filename

                env_vars = {
                    **os.environ,
                    'TEMP_BUILD_DIR': str(temp_path),
                    'HTML_FILENAME': html_filename,
                    'CSS_FILENAME': css_filename
                }


                process = subprocess.Popen(
                    ["npm", "run", "build"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env_vars
                )
                stdout, stderr = process.communicate(timeout=30)

                if process.returncode == 0:
                    if css_output_path.exists():
                        with open(css_output_path, "r") as f:
                            css_content = f.read()
                    else:
                        raise Exception("CSS file not generated")
                else:
                    raise Exception(f"Build failed: {stderr.decode()}")

            return css_content

        except subprocess.TimeoutExpired:
            raise Exception("Build process timed out")
        except Exception as e:
            raise Exception(f"Build error: {str(e)}")

class UploadHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.builder = TailwindBuilder()

    def validate_file(self, file_info):
        if not file_info:
            raise ValueError("No file provided")

        filename = file_info['filename']
        content_length = len(file_info['body'])

        if content_length > Config.MAX_UPLOAD_SIZE:
            raise ValueError(f"File size exceeds maximum limit of {Config.MAX_UPLOAD_SIZE // 1024}KB")

        if not any(filename.lower().endswith(ext) for ext in Config.ALLOWED_EXTENSIONS):
            raise ValueError("Invalid file type. Only HTML files are allowed")

    async def post(self):
        try:

            file_info = self.request.files.get('htmlFile', [None])[0]
            self.validate_file(file_info)

            html_content = file_info['body'].decode('utf-8')

            css_content = self.builder.build_css(html_content)

            self.set_header('Content-Type', 'text/css')
            self.set_header('Content-Disposition', 'attachment; filename=styles.css')

            self.write(css_content)

        except ValueError as e:
            self.set_status(400)
            self.write({
                "success": False,
                "message": str(e)
            })
        except Exception as e:
            self.set_status(500)
            self.write({
                "success": False,
                "message": f"Server error: {str(e)}"
            })

def make_app():
    enable_pretty_logging()
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/upload", UploadHandler),
    ],
    template_path="templates",
    static_path="static",
    debug=True)

if __name__ == "__main__":
    app = make_app()
    app.listen(5000,xheaders=True)
    tornado.ioloop.IOLoop.current().start()
