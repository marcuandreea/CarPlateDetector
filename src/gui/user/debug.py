class UserDebugMixin:
    # Debug mode toggle
    def on_debug_toggled(self, _checked):
        entry_thread = getattr(self, "entry_scanner_thread", None)
        if entry_thread and entry_thread.isRunning():
            if getattr(self, "entry_source", "live") == "live":
                self.stop_entry_live_scanner()
                self.start_entry_live_scanner()
            else:
                video_path = getattr(self, "last_entry_video_path", None)
                if video_path:
                    self.stop_entry_live_scanner()
                    self.start_entry_video_scanner(video_path)

        qr_thread = getattr(self, "qr_scanner_thread", None)
        if qr_thread and qr_thread.isRunning():
            qr_target = getattr(self, "current_qr_target", None)
            self.stop_qr_scanner()
            if qr_target:
                self.start_qr_scanner(qr_target)
