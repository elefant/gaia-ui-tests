# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import pprint
import time

from marionette.by import By
from gaiatest.apps.base import Base
from gaiatest import GaiaTestCase
from marionette import Marionette

class SystemMessage(Base):
    name = "Test Container"
    def launch(self):
        Base.launch(self)

class TestSystemMessages(GaiaTestCase):
    TESTING_SYSTEM_MESSAGE   = 'dummy-message'
    TESTING_MESSAGE_LABEL_ID = 'message'
    TESTING_MESSAGE_PATTERN  = 'This is system message test powered by gaia-ui-tests'

    # Two basic functions are tested here:
    # 1. The testing app must be launched after broadcasting the testing system message
    # 2. The testing app must show the same text we broadcast together with the message
    def test_app_launched(self):
        self.app = SystemMessage(self.marionette)
        self.app.url = self.get_testing_app_url()

        # Make sure the testing app has been killed
        self.apps.kill_all()
        runningApps = self.apps.runningApps()
        for app in runningApps:
            self.assertTrue(-1 == self.app.url.find(app))

        # Broadcast system message
        self.broadcast_system_message(self.TESTING_MESSAGE_PATTERN)
        time.sleep(2) # Wait some time to prevent from long launching time

        # Make sure the testing app is running now
        runningApps = self.apps.runningApps()
        found = False
        for app in runningApps:
            if -1 != self.app.url.find(app):
                found = True
                break
        self.assertTrue(found)

        # We've made sure app is running.
        # Now test if the message is delivered correctly to the app
        self.app.launch()
        self.on_app_launched()
        message = self.marionette.find_element(By.ID, self.TESTING_MESSAGE_LABEL_ID)
        self.assertEqual(message.text, self.TESTING_MESSAGE_PATTERN)

    def get_testing_app_url(self):
        self.app.launch()
        url = self.marionette.get_url()
        self.assertTrue(len(url) > 0)
        return url

    def broadcast_system_message(self, msg):
        self.marionette.set_context("chrome")
        self.marionette.execute_script("""
          const { classes: Cc, interfaces: Ci, utils: Cu, results: Cr } = Components;
          let messenger = Cc["@mozilla.org/system-message-internal;1"]
                          .getService(Ci.nsISystemMessagesInternal);
          messenger.broadcastMessage("%s", {value: "%s"}, {});
        """ % (self.TESTING_SYSTEM_MESSAGE, msg))
        self.marionette.set_context("content")

    # Injest some javscript to test if the message is delivered
    def on_app_launched(self):
        self.marionette.execute_script("""
            navigator.mozSetMessageHandler("%s", function(msg) {
              var messageLabel = document.createElement("label");
              messageLabel.id = "%s";
              messageLabel.innerHTML = msg.value;
              let container = document.getElementById('test-container');
              document.body.insertBefore(messageLabel, container);
            });
        """ % (self.TESTING_SYSTEM_MESSAGE, self.TESTING_MESSAGE_LABEL_ID))