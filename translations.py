import locale


class Translator:
    def __init__(self):
        self.lang = "it" if "it" in locale.getdefaultlocale()[0] else "en"
        print(f"Language detected: {self.lang}")

    def translate(self, msg: str, *args) -> str:
        if msg not in self.translations:
            raise Exception(f"Message {msg} is not available.")
        else:
            return self.translations[msg][self.lang].format(*args)

    translations = {
        'choose_button': {
            'it': "Scegli file e/o cartelle",
            'en': "Choose files and/or directories",
        },
        'no_files_selected': {
            'it': "Non hai selezionato alcun file o cartella!\n\n",
            'en': "You haven't selected any file or directory!\n\n",
        },
        'starting_text': {
            'it': "{}Scegli la cartella di un esame per ottenere una stima di quanto tempo serva per studiarlo.",
            'en': "{}Choose an exam directory to get an estimation of the time required to study its contents.",
        },
        'waiting': {
            'it': "Attendo che tu scelga qualche file o cartella...",
            'en': "Waiting for you to choose some files or directories...",
        },
        'time_per_page': {
            'it': "Tempo per pagina",
            'en': "Time per page",
        },
        'video_speed': {
            'it': "Velocità di riproduzione",
            'en': "Video speed",
        },
        'hours_per_day': {
            'it': "Ore al giorno",
            'en': "Hours per day",
        },
        'documents': {
            'it': "Documenti",
            'en': "Documents",
        },
        'videos': {
            'it': "Video",
            'en': "Videos",
        },
        'total': {
            'it': "Totale",
            'en': "Total",
        },
        'preparation': {
            'it': "Preparazione",
            'en': "Preparation",
        },
        'no_docs': {
            'it': "Sembra che non ci siano pdf da studiare nelle cartelle selezionate.\n",
            'en': "It seems there are no pdfs to study in the given directories.\n",
        },
        'docs_text': {
            'it': "Ci sono <b>{}</b> pagine di pdf da studiare nelle cartelle selezionate tra <b>{}</b> file.\nA "
                  "<b>{}</b> per pagina, ci impiegherai <b>{}</b> a studiare questi documenti.\n",
            'en': "There are <b>{}</b> pdf pages to study in the given directories spanning <b>{}</b> files.\nAt "
                  "<b>{}</b> per page, it will take you <b>{}</b> to study these documents.\n",
        },
        'pdf_error': {
            'it': "\nSembra che alcuni documenti pdf non si siano aperti correttamente, sono stati saltati.\n",
            'en': "\nIt seems some PDF documents could not be opened correctly, they have been skipped.\n",
        },
        'no_videos': {
            'it': "Sembra che non ci siano videolezioni da guardare nelle cartelle selezionate.\n",
            'en': "It seems there are no video lectures to watch in the given directories.\n",
        },
        'vids_text': {
            'it': "Ci sono <b>{}</b> da guardare nelle cartelle selezionate divisi tra <b>{}</b> video.\n A <b>{}</b> "
                  "ci impiegherai <b>{}</b> a finire.\n",
            'en': "There are <b>{}</b> to watch in the given directories divided between <b>{}</b> videos.\nAt "
                  "<b>{}x</b> it will take you <b>{}</b> to finish.\n",
        },
        'video_error': {
            'it': "\nSembra che alcuni video non si siano aperti correttamente, sono stati saltati.\n",
            'en': "\nIt seems some video files could not be opened correctly, they have been skipped.\n",
        },
        'tot_text': {
            'it': "In totale, ci impiegherai <b>{}</b> a studiare tutto tra i file e le cartelle selezionate.\n",
            'en': "In total, it will take you <b>{}</b> to study everything in the given files or directories.\n",
        },
        'prep_text': {
            'it': "Studiando <b>{} ora/e</b> ogni giorno, ci impiegherai circa <b>{} giorno/i</b> a preparare questo "
                  "esame.\n",
            'en': "Studying <b>{} hour(s)</b> every day, it will take you around <b>{} day(s)</b> to prepare for this "
                  "exam.\n",
        }
    }
