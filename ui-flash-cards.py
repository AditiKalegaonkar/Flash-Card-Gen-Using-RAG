import flet as ft
import os
import json
import ast
import RAG as rag  # Your backend logic

def load(file_path):
    docs = rag.load_and_chunk(file_path)
    return generate_flashcards(docs)

def generate_flashcards(docs):
    ans = rag.pipeline(docs)
    if isinstance(ans, dict):
        return ans
    elif isinstance(ans, str):
        try:
            return json.loads(ans)
        except json.JSONDecodeError:
            try:
                return ast.literal_eval(ans)
            except (SyntaxError, ValueError):
                result = {}
                cleaned_str = ans.strip()
                if cleaned_str.startswith('{') and cleaned_str.endswith('}'):
                    cleaned_str = cleaned_str[1:-1]
                pairs = cleaned_str.split('\n') if '\n' in cleaned_str else cleaned_str.split(',')
                for pair in pairs:
                    if ':' in pair:
                        key, value = pair.split(':', 1)
                        key = key.strip().strip('"\'')
                        value = value.strip().strip('"\'')
                        result[key] = value
                return result
    return {}

def main(page: ft.Page):
    page.title = "Flashcards Maker"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.window_width = 600
    page.window_height = 800
    page.bgcolor = ft.colors.WHITE
    page.vertical_alignment = ft.MainAxisAlignment.START

    flashcards = []
    current_index = 0
    flipped = False

    page.add(
        ft.Column([
            ft.Text(
                "Interactive Flashcard Generator",
                size=30,
                weight=ft.FontWeight.BOLD,
                color=ft.colors.ORANGE,
                text_align=ft.TextAlign.CENTER
            ),
            ft.Text(
                "Upload a PDF file to generate interactive flashcards",
                size=16,
                italic=True,
                color=ft.colors.GREY,
                text_align=ft.TextAlign.CENTER
            )
        ],
        spacing=5,
        alignment=ft.MainAxisAlignment.CENTER)
    )

    def file_picker_result(e: ft.FilePickerResultEvent):
        if e.files:
            file_paths.value = e.files[0].path
            file_name.value = e.files[0].name
            page.update()

    file_picker = ft.FilePicker(on_result=file_picker_result)
    page.overlay.append(file_picker)

    file_paths = ft.TextField(label="PDF file path", read_only=True, expand=True)
    file_name = ft.Text(size=14, color=ft.colors.GREY)

    flashcard_container = ft.Container(
        content=ft.Column([
            ft.Text("Select a PDF file to start",
                    size=18,
                    color=ft.colors.GREY,
                    text_align=ft.TextAlign.CENTER)
        ], alignment=ft.MainAxisAlignment.CENTER),
        width=500,
        height=300,
        bgcolor=ft.colors.GREY_200,
        border_radius=10,
        padding=20,
        alignment=ft.alignment.center,
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.colors.BLACK12),
        on_click=lambda e: flip_card(e),
        ink=True
    )

    counter_text = ft.Text("", size=14, color=ft.colors.GREY)
    progress_bar = ft.ProgressBar(width=500, color=ft.colors.ORANGE, bgcolor=ft.colors.GREY_300, visible=False)

    def update_flashcard_display():
        nonlocal flashcards, current_index, flipped
        if not flashcards:
            flashcard_container.content = ft.Column([
                ft.Text("No flashcards available",
                        size=18,
                        color=ft.colors.GREY,
                        text_align=ft.TextAlign.CENTER)
            ], alignment=ft.MainAxisAlignment.CENTER)
            counter_text.value = ""
            next_button.disabled = True
            prev_button.disabled = True
        else:
            question, answer = flashcards[current_index]
            if flipped:
                flashcard_container.content = ft.Column([
                    ft.Text("Answer:", size=16, color=ft.colors.GREY),
                    ft.Container(content=ft.Text(answer, size=20, color=ft.colors.BLACK), padding=10)
                ], alignment=ft.MainAxisAlignment.CENTER)
                flashcard_container.bgcolor = ft.colors.GREEN_50
            else:
                flashcard_container.content = ft.Column([
                    ft.Text("Question:", size=16, color=ft.colors.GREY),
                    ft.Container(content=ft.Text(question, size=20, color=ft.colors.BLACK, weight=ft.FontWeight.BOLD), padding=10)
                ], alignment=ft.MainAxisAlignment.CENTER)
                flashcard_container.bgcolor = ft.colors.GREY_200

            counter_text.value = f"Card {current_index + 1} of {len(flashcards)}"
            next_button.disabled = current_index >= len(flashcards) - 1
            prev_button.disabled = current_index <= 0
        page.update()

    def load_flashcards(e):
        nonlocal flashcards, current_index, flipped
        file_path = file_paths.value
        if file_path and os.path.isfile(file_path) and file_path.lower().endswith(".pdf"):
            progress_bar.visible = True
            page.update()
            cards = load(file_path)
            progress_bar.visible = False
            if cards and isinstance(cards, dict):
                flashcards = list(cards.items())
                current_index = 0
                flipped = False
                update_flashcard_display()
            else:
                flashcard_container.content = ft.Column([
                    ft.Text("No valid flashcards generated",
                            size=18,
                            color=ft.colors.RED,
                            text_align=ft.TextAlign.CENTER)
                ], alignment=ft.MainAxisAlignment.CENTER)
                page.update()

    def flip_card(e):
        nonlocal flipped
        if flashcards:
            flipped = not flipped
            update_flashcard_display()

    def previous_card(e):
        nonlocal current_index, flipped
        if current_index > 0:
            current_index -= 1
            flipped = False
            update_flashcard_display()

    def next_card(e):
        nonlocal current_index, flipped
        if current_index < len(flashcards) - 1:
            current_index += 1
            flipped = False
            update_flashcard_display()

    browse_button = ft.ElevatedButton(
        "Browse...", icon=ft.icons.FOLDER_OPEN,
        on_click=lambda _: file_picker.pick_files(allowed_extensions=["pdf"])
    )

    load_button = ft.ElevatedButton(
        "Generate Flashcards",
        icon=ft.icons.AUTO_AWESOME,
        on_click=load_flashcards,
        style=ft.ButtonStyle(color=ft.colors.WHITE, bgcolor=ft.colors.ORANGE)
    )

    prev_button = ft.ElevatedButton(
        "Previous", icon=ft.icons.ARROW_BACK,
        on_click=previous_card, disabled=True,
        style=ft.ButtonStyle(
            color=ft.colors.ORANGE,
            bgcolor=ft.colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=8),
            side=ft.BorderSide(width=2, color=ft.colors.ORANGE),
        )
    )

    next_button = ft.ElevatedButton(
        "Next", icon=ft.icons.ARROW_FORWARD,
        on_click=next_card, disabled=True,
        style=ft.ButtonStyle(
            color=ft.colors.WHITE,
            bgcolor=ft.colors.ORANGE,
            shape=ft.RoundedRectangleBorder(radius=8),
        )
    )

    def update_button_states():
        if flashcards:
            next_button.disabled = current_index >= len(flashcards) - 1
            prev_button.disabled = current_index <= 0
        else:
            next_button.disabled = True
            prev_button.disabled = True
        page.update()

    # Layout
    page.add(
        ft.Container(height=20),
        ft.Row([file_paths, browse_button], alignment=ft.MainAxisAlignment.CENTER),
        file_name,
        ft.Container(height=10),
        load_button,
        ft.Container(height=5),
        progress_bar,
        ft.Container(height=20),

        # Centered flashcard
        ft.Row([flashcard_container], alignment=ft.MainAxisAlignment.CENTER),

        ft.Container(height=10),
        counter_text,
        ft.Container(height=10),
        ft.Row([prev_button, next_button], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
    )

    update_button_states()

if __name__ == "__main__":
    ft.app(target=main)
