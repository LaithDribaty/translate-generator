from datetime import timedelta
import os
import whisper
import argostranslate.package
import argostranslate.translate


def transcribe_audio(output_srt_path, file_name):
    model = whisper.load_model("small")  # Change this to your desired model
    
    transcribe_result = model.transcribe(audio=f"{file_name}", language="de")

    segments = transcribe_result['segments']

    germans = [segment['text'][1:] if segment['text'][0] == ' ' else segment['text'] for segment in segments ]
    
    # install models before running the script
    # argostranslate.package.install_from_path("./translate-de_en-1_0.argosmodel")
    # argostranslate.package.install_from_path("./translate-en_de-1_0.argosmodel")
    translations = [argostranslate.translate.translate(sentence, "de", "en") for sentence in germans]

    with open(output_srt_path, 'w', encoding='utf-8') as srt_file:
        for idx, segment in enumerate(segments):
            try:
                start_time = str(timedelta(seconds=int(segment['start']))) + ',000'
                end_time = str(timedelta(seconds=int(segment['end']))) + ',000'

                text = segment['text']
                segment_id = segment['id'] + 1
                srt_segment = f"{segment_id}\\n{start_time} --> {end_time}\\n{text[1:] if text[0] == ' ' else text}\\n"
                srt_file.write(srt_segment)
                
                text = ''.join(['-' for _ in range(min(80, len(segment['text']) + 10))])
                srt_segment = f"{text}\\n"
                srt_file.write(srt_segment)
                
                english_translation = translations[segment['id']]
                srt_segment = f"{english_translation}\\n\\n"
                srt_file.write(srt_segment)
            except Exception as e:
                print(e)

    return output_srt_path

translated = set()
for file_name in os.listdir('./'):
    if file_name.endswith(".srt"):
        translated.add(f"{file_name[:-4]}")

for file_name in os.listdir('./'):
    if not file_name.endswith(".mp4"):
        continue
    if file_name in translated:
        continue

    # Example usage: Convert "audio.mp3" to an SRT file
    # don't forget to replace \n with a real new line
    output_srt_path = f"{file_name}.srt"

    transcribe_audio(output_srt_path, file_name)
    print(f"Transcription saved to {output_srt_path}")
