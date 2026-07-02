class AdminTabsMixin:
    def refresh_admin_tab(self):
        # Reincarca continutul tabului admin curent
        current_tab = getattr(self, 'current_admin_tab', 'masini')

        if hasattr(self, 'add_taxa_btn'):
            if current_tab == 'taxe':
                self.add_taxa_btn.setText('Adauga Taxa Noua')
                self.add_taxa_btn.show()
            elif current_tab == 'subscriptions':
                self.add_taxa_btn.setText("Adauga Abonament Nou")
                self.add_taxa_btn.show()
            else:
                self.add_taxa_btn.hide()

        if current_tab == 'masini':
            self.handle_show_masini()
        elif current_tab == 'taxe':
            self.handle_show_taxe()
        elif current_tab == 'subscriptions':
            self.handle_show_subscriptions()
        elif current_tab == 'user_subscriptions':
            self.handle_show_user_subscriptions()
        elif current_tab == 'users':
            self.handle_show_users()

    def handle_add_action(self):
        # Dispatch pentru butonul de adaugare in functie de tabul activ
        current_tab = getattr(self, 'current_admin_tab', 'masini')
        if current_tab == 'taxe':
            self.handle_add_taxa()
        elif current_tab == 'subscriptions':
            self.handle_add_subscription_plan()
