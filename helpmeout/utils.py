import os
from moviepy.editor import VideoFileClip, concatenate_videoclips

def append_video(recording_id):
    # Get the directory name
    dir_name = f"helpmeout/static/{recording_id}"

    clips = [
        VideoFileClip(os.path.join(dir_name, filename))
        for filename in os.listdir(dir_name)
    ]
    # Concatenate the video clips
    if len(clips) == 1:
        final_clip = clips[0]
    else:
        final_clip = concatenate_videoclips(clips, method="compose")

    # Save the concatenated video to a file
    final_clip.write_videofile(f"helpmeout/static/{recording_id}.mp4", codec="libx264")

    # Delete the directory forcefully
    os.system(f"rm -rf {dir_name}")

    return final_clip


async def get_transcript(id):
    deepgram = Deepgram(DEEPGRAM_API_KEY)
    recording = Recordings.query.filter_by(id=id).first()
    if not recording:
        return jsonify({'error': 'recording not found'}), 404
    if not recording.transcript:
        # if {id}.mp4 does not exist then return recording is empty
        if not os.path.exists(f"helpmeout/static/{id}.mp4"):
            return jsonify({'error': 'recording not ready'}), 404

        # Convert video to audio
        audio = VideoFileClip(f"helpmeout/static/{id}.mp4").audio
        audio_file_path = f"helpmeout/static/{id}.mp3"
        audio.write_audiofile(audio_file_path)

        # Transcribe audio using Deepgram
        PARAMS = {'punctuate': True, 'tier': 'enhanced'}
        with open(audio_file_path, 'rb') as audio_file:
            source = {'buffer': audio_file, 'mimetype': 'audio/mp3'}
            data = await deepgram.transcription.prerecorded(source, PARAMS)
            recording.transcript = json.dumps(data['results']['channels'][0]['alternatives'][0], indent=2)
            db.session.commit()

    # Return the transcript as JSON
    return Response(recording.transcript, mimetype='application/json'), 200

