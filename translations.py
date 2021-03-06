import locale
from sys import stderr


class Translator:
    def __init__(self):
        self.lang = "it" if "it" in locale.getdefaultlocale()[0] else "en"
        print(f"Language detected: {self.lang}")

    def translate(self, msg: str, *args) -> str:
        if msg not in self.translations:
            raise Exception(f"Message {msg} is not available.")
        else:
            return self.translations[msg][self.lang].format(*args)

    def human_readable_time(self, seconds) -> str:
        if seconds < 0:
            print("An error occurred due to negative time being calculated. Please try again.", file=stderr)
            exit(-1)
        elif 0 <= seconds < 60:
            if seconds == 1:
                return f"{seconds} second" if self.lang == 'en' else f"{seconds} secondo"
            else:
                return f"{seconds} seconds" if self.lang == 'en' else f"{seconds} secondi"
        elif 60 <= seconds < 3600:
            minutes = int(seconds // 60)
            remainder = int(seconds % 60)
            if minutes == 1:
                res = f"{minutes} minute" if self.lang == 'en' else f"{minutes} minuto"
            else:
                res = f"{minutes} minutes" if self.lang == 'en' else f"{minutes} minuti"
            if remainder == 1:
                res += f" and {remainder} second" if self.lang == 'en' else f" e {remainder} secondo"
            elif remainder > 1:
                res += f" and {remainder} seconds" if self.lang == 'en' else f" e {remainder} secondi"
            return res
        elif seconds >= 3600:
            hours = int(seconds // 3600)
            minutes = int(seconds % 3600) // 60
            if hours == 1:
                res = f"{hours} hour" if self.lang == 'en' else f"{hours} ora"
            else:
                res = f"{hours} hours" if self.lang == 'en' else f"{hours} ore"
            if minutes == 1:
                res += f" and {minutes} minute" if self.lang == 'en' else f" e {minutes} minuto"
            elif minutes > 1:
                res += f" and {minutes} minutes" if self.lang == 'en' else f" e {minutes} minuti"
            return res

    def get_hours(self, hours: int) -> str:
        if hours == 1:
            return f"{hours} hour" if self.lang == 'en' else f"{hours} ora"
        else:
            return f"{hours} hours" if self.lang == 'en' else f"{hours} ore"

    def get_days(self, days: int) -> str:
        if days == 1:
            return f"{days} day" if self.lang == 'en' else f"{days} giorno"
        else:
            return f"{days} days" if self.lang == 'en' else f"{days} giorni"

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
            'it': "Studiando <b>{}</b> ogni giorno, ci impiegherai circa <b>{}</b> a preparare questo "
                  "esame.\n",
            'en': "Studying <b>{}</b> every day, it will take you around <b>{}</b> to prepare for this "
                  "exam.\n",
        }
    }
