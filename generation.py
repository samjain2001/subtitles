from flask import Flask, render_template, send_from_directory
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
import logging
from wtforms.validators import InputRequired
from deepgram import Deepgram
import json
import pysrt
from config import DEEPGRAM_API_KEY

file_response = ''

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/files'

font_directory = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static')
os.environ['MAGICK_FONT_PATH'] = font_directory

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")

def time_to_seconds(time_obj):
    return time_obj.hours * 3600 + time_obj.minutes * 60 + time_obj.seconds + time_obj.milliseconds / 1000

def create_subtitle_clips(subtitles, videosize, fontsize=24, font='Arial.ttf', color='yellow', debug=False):
    font_with_path = os.path.join(font_directory, font)
    subtitle_clips = []
    
    for subtitle in subtitles:
        start_time = time_to_seconds(subtitle.start)
        end_time = time_to_seconds(subtitle.end)
        duration = end_time - start_time
        video_width, video_height = videosize
        text_clip = TextClip(subtitle.text, fontsize=fontsize, font=font_with_path, color=color, bg_color='black', size=(video_width * 3 / 4, None), method='caption').set_start(start_time).set_duration(duration)
        subtitle_x_position = 'center'
        subtitle_y_position = video_height * 4 / 5
        text_position = (subtitle_x_position, subtitle_y_position)
        subtitle_clips.append(text_clip.set_position(text_position))
    return subtitle_clips

def processFile(filePath):
    PATH_TO_FILE = filePath
    MIMETYPE = 'audio/wav'
    global file_response

    def init_deepgram():
        global file_response
        dg_client = Deepgram(DEEPGRAM_API_KEY)
        with open(PATH_TO_FILE, 'rb') as audio:
            source = {'buffer': audio, 'mimetype': MIMETYPE}
            options = {"punctuate": True, "model": "nova", "language": "en-US"}
            file_response = dg_client.transcription.sync_prerecorded(source, options)
            print('json response:')
            print(json.dumps(file_response, indent=4))

    init_deepgram()
    subtitle_data = file_response['results']['channels'][0]['alternatives'][0]['words']
    print(subtitle_data)

    filename = os.path.basename(filePath)
    name, extension = os.path.splitext(filename)
    op_file = name + ".srt"
    print('output filename')
    print(op_file)

    output_video_file = 'static/files/output.mp4'  # Define output_video_file here
    mp4filename = filePath
    srtfilename = op_file

    def convert_to_srt(data, op_file):
        def format_time(seconds):
            hours, remainder = divmod(seconds, 3600)
            minutes, remainder = divmod(remainder, 60)
            seconds, milliseconds = divmod(remainder, 1)
            return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},{int(milliseconds * 1000):03d}"

        with open(op_file, 'w') as f:
            for i, entry in enumerate(data, start=1):
                start_time = format_time(entry['start'])
                end_time = format_time(entry['end'])
                subtitle_text = entry['punctuated_word']
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{subtitle_text}\n\n")

    convert_to_srt(subtitle_data, op_file)
    mp4filename = filePath
    srtfilename = op_file

    video = VideoFileClip(mp4filename)
    subtitles = pysrt.open(srtfilename)
    subtitle_clips = create_subtitle_clips(subtitles, video.size)
    ffmpeg_params = [
        "-y", "-f", "image2pipe", "-c:v", "png", "-r", "30", "-i", "-", "-c:v", "libx264",
        "-crf", "18", "-preset", "slow", output_video_file
    ]
    # Concatenate the subtitle clips with the original video
    final_video = CompositeVideoClip([video] + subtitle_clips, size=video.size).set_audio(video.audio)

    final_video.fps = video.fps

    ffmpeg_logger = logging.getLogger("FFMPEG")
    ffmpeg_logger.setLevel(logging.DEBUG)

    ffmpeg_handler = logging.StreamHandler()
    ffmpeg_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ffmpeg_handler.setFormatter(formatter)

    ffmpeg_logger.addHandler(ffmpeg_handler)

    # Set the output video file path
    output_video_file = 'static/files/output.mp4'

    # Define ffmpeg parameters for video processing
    ffmpeg_params = [
        "-y", "-f", "image2pipe", "-c:v", "png", "-r", "30", "-i", "-",
        "-c:v", "libx264", "-crf", "18", "-preset", "slow", output_video_file
    ]
    final_video.write_videofile(output_video_file, codec="libx264", audio_codec="aac", logger=lambda msg: ffmpeg_logger.info(msg), temp_audiofile="temp-audio.m4a", remove_temp=True, ffmpeg_params=ffmpeg_params)

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
        processFile(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
        return render_template('play_video.html')
    return render_template('video_upload.html', form=form)

@app.route('/download')
def download_file():
    filename = 'output.mp4'
    return send_from_directory(os.path.join(app.root_path, app.config['UPLOAD_FOLDER']), filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
