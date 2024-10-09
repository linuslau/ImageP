from PyQt5.QtCore import QTimer


def handle_click():
    print("Sync handle click processed")
    from ImageP.imgproc.ortho_view import start_ortho_view
    QTimer.singleShot(0, lambda: start_ortho_view())
