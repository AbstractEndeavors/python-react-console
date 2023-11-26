class AbstractBrowser:
    # Existing __init__ and other methods...

    def __init__(self, window_mgr=None, window_name=None, window=None):
        # Existing initializations...
        self.directory_scanner = DirectoryScanner(os.getcwd(), self.get_approved_paths())
        self.react_mgr = ReactManager(window_mgr=self.window_mgr)
        # Rest of the initialization...

    def scan_it(self, directory):
        # Use DirectoryScanner to perform the scan
        self.directory_scanner.base_path = directory
        self.directory_scanner.scan()  # This will run the scan in a separate thread

        # You may need logic to update the UI with scan results once the scan is complete

    def handle_event(self, event, values, window):
        # Existing logic...
        # Add logic to handle ReactManager related events
        self.react_mgr.while_it(event, values, window)

        # Rest of the event handling logic...

# ReactManager class remains the same
# DirectoryScanner class remains the same

# Instantiate AbstractBrowser and run the main loop
abstract_browser = AbstractBrowser()
abstract_browser.run_main_loop()  #
