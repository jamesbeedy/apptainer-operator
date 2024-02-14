#!/usr/bin/env python3
# Copyright 2024 Omnivector, LLC.
# See LICENSE file for licensing details.

"""ApptainerOperatorCharm."""
from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus, WaitingStatus

from apptainer import Apptainer


class ApptainerOperatorCharm(CharmBase):
    """Apptainer Operator lifecycle events."""

    def __init__(self, *args, **kwargs):
        """Init _stored attributes and interfaces, observe events."""
        super().__init__(*args, **kwargs)

        event_handler_bindings = {
            self.on.install: self._on_install,
            self.on.update_status: self._update_status,
            self.on.removed: self._on_uninstall,
            self.on.upgrade_action: self._on_upgrade_apptainer,
        }
        for event, handler in event_handler_bindings.items():
            self.framework.observe(event, handler)

    def _set_workload_version(self):
        """Set the charmed workload version."""
        apptainer_version = apptainer.version()
        self.unit.set_workload_version(apptainer_version)
        self.unit.status = ActiveStatus(f"Apptainer version: {apptainer_version} installed")

    def _on_install(self, event):
        """Perform installation operations for apptainer."""
        apptainer = Apptainer()
        try:
            self.unit.status = WaitingStatus("Installing apptainer")
            apptainer.install()
            self.unit.status = ActiveStatus("Apptainer installed")
        except Exception as e:
            self.unit.status = BlockedStatus("Trouble installing apptainer, please debug.")
            event.defer()
            return
        # Set the workload version
        self._set_workload_version()

    def _on_uninstall(self, event):
        """Perform uninstallation operations for apptainer."""
        apptainer = Apptainer()
        try:
            self.unit.status = WaitingStatus("Uninstalling apptainer")
            apptainer.uninstall()
        except Exception as e:
            self.unit.status = BlockedStatus("Trouble uninstalling apptainer, please debug.")
            event.defer()
            return

    def _on_upgrade_apptainer(self, event):
        """Perform upgrade to latest operations."""
        apptainer = Apptainer()
        apptainer.upgrade_to_latest()
        # Set the workload version
        self._set_workload_version()


if __name__ == "__main__":  # pragma: nocover
    main(ApptainerOperatorCharm)
