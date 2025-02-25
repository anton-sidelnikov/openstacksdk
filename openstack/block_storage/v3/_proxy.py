# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from openstack.block_storage import _base_proxy
from openstack.block_storage.v3 import availability_zone
from openstack.block_storage.v3 import backup as _backup
from openstack.block_storage.v3 import capabilities as _capabilities
from openstack.block_storage.v3 import extension as _extension
from openstack.block_storage.v3 import group_type as _group_type
from openstack.block_storage.v3 import limits as _limits
from openstack.block_storage.v3 import quota_set as _quota_set
from openstack.block_storage.v3 import resource_filter as _resource_filter
from openstack.block_storage.v3 import snapshot as _snapshot
from openstack.block_storage.v3 import stats as _stats
from openstack.block_storage.v3 import type as _type
from openstack.block_storage.v3 import volume as _volume
from openstack import exceptions
from openstack.identity.v3 import project as _project
from openstack import resource


class Proxy(_base_proxy.BaseBlockStorageProxy):

    # ====== SNAPSHOTS ======
    def get_snapshot(self, snapshot):
        """Get a single snapshot

        :param snapshot: The value can be the ID of a snapshot or a
            :class:`~openstack.block_storage.v3.snapshot.Snapshot`
            instance.

        :returns: One :class:`~openstack.block_storage.v3.snapshot.Snapshot`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
            when no resource can be found.
        """
        return self._get(_snapshot.Snapshot, snapshot)

    def find_snapshot(self, name_or_id, ignore_missing=True, **attrs):
        """Find a single snapshot

        :param snapshot: The name or ID a snapshot
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the snapshot does not exist.

        :returns: One :class:`~openstack.block_storage.v3.snapshot.Snapshot`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
            when no resource can be found.
        """
        return self._find(_snapshot.Snapshot, name_or_id,
                          ignore_missing=ignore_missing)

    def snapshots(self, details=True, **query):
        """Retrieve a generator of snapshots

        :param bool details: When set to ``False`` :class:
            `~openstack.block_storage.v3.snapshot.Snapshot`
            objects will be returned. The default, ``True``, will cause
            more attributes to be returned.
        :param kwargs query: Optional query parameters to be sent to limit
            the snapshots being returned.  Available parameters include:

            * name: Name of the snapshot as a string.
            * all_projects: Whether return the snapshots in all projects.
            * project_id: Filter the snapshots by project.
            * volume_id: volume id of a snapshot.
            * status: Value of the status of the snapshot so that you can
              filter on "available" for example.

        :returns: A generator of snapshot objects.
        """
        base_path = '/snapshots/detail' if details else None
        return self._list(_snapshot.Snapshot, base_path=base_path, **query)

    def create_snapshot(self, **attrs):
        """Create a new snapshot from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.block_storage.v3.snapshot.Snapshot`,
            comprised of the properties on the Snapshot class.

        :returns: The results of snapshot creation
        :rtype: :class:`~openstack.block_storage.v3.snapshot.Snapshot`
        """
        return self._create(_snapshot.Snapshot, **attrs)

    def delete_snapshot(self, snapshot, ignore_missing=True, force=False):
        """Delete a snapshot

        :param snapshot: The value can be either the ID of a snapshot or a
            :class:`~openstack.block_storage.v3.snapshot.Snapshot` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be
            raised when the snapshot does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent snapshot.
        :param bool force: Whether to try forcing snapshot deletion.

        :returns: ``None``
        """
        if not force:
            self._delete(
                _snapshot.Snapshot, snapshot, ignore_missing=ignore_missing)
        else:
            snapshot = self._get_resource(_snapshot.Snapshot, snapshot)
            snapshot.force_delete(self)

    # ====== SNAPSHOT ACTIONS ======
    def reset_snapshot(self, snapshot, status):
        """Reset status of the snapshot

        :param snapshot: The value can be either the ID of a backup or a
            :class:`~openstack.block_storage.v3.snapshot.Snapshot` instance.
        :param str status: New snapshot status

        :returns: None
        """
        snapshot = self._get_resource(_snapshot.Snapshot, snapshot)
        snapshot.reset(self, status)

    def set_snapshot_status(self, snapshot, status, progress=None):
        """Update fields related to the status of a snapshot.

        :param snapshot: The value can be either the ID of a backup or a
            :class:`~openstack.block_storage.v3.snapshot.Snapshot` instance.
        :param str status: New snapshot status
        :param str progress: A percentage value for snapshot build progress.

        :returns: None
        """
        snapshot = self._get_resource(_snapshot.Snapshot, snapshot)
        snapshot.set_status(self, status, progress)

    # ====== TYPES ======
    def get_type(self, type):
        """Get a single type

        :param type: The value can be the ID of a type or a
            :class:`~openstack.block_storage.v3.type.Type` instance.

        :returns: One :class:`~openstack.block_storage.v3.type.Type`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
            when no resource can be found.
        """
        return self._get(_type.Type, type)

    def find_type(self, name_or_id, ignore_missing=True, **attrs):
        """Find a single volume type

        :param snapshot: The name or ID a volume type
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the type does not exist.

        :returns: One :class:`~openstack.block_storage.v3.type.Type`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
            when no resource can be found.
        """
        return self._find(_type.Type, name_or_id,
                          ignore_missing=ignore_missing)

    def types(self, **query):
        """Retrieve a generator of volume types

        :returns: A generator of volume type objects.
        """
        return self._list(_type.Type, **query)

    def create_type(self, **attrs):
        """Create a new type from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.block_storage.v3.type.Type`,
            comprised of the properties on the Type class.

        :returns: The results of type creation
        :rtype: :class:`~openstack.block_storage.v3.type.Type`
        """
        return self._create(_type.Type, **attrs)

    def delete_type(self, type, ignore_missing=True):
        """Delete a type

        :param type: The value can be either the ID of a type or a
            :class:`~openstack.block_storage.v3.type.Type` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be
            raised when the type does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent type.

        :returns: ``None``
        """
        self._delete(_type.Type, type, ignore_missing=ignore_missing)

    def update_type(self, type, **attrs):
        """Update a type

        :param type: The value can be either the ID of a type or a
            :class:`~openstack.block_storage.v3.type.Type` instance.
        :param dict attrs: The attributes to update on the type
            represented by ``value``.

        :returns: The updated type
        :rtype: :class:`~openstack.block_storage.v3.type.Type`
        """
        return self._update(_type.Type, type, **attrs)

    def update_type_extra_specs(self, type, **attrs):
        """Update the extra_specs for a type

        :param type: The value can be either the ID of a type or a
            :class:`~openstack.block_storage.v3.type.Type` instance.
        :param dict attrs: The extra_spec attributes to update on the
            type represented by ``value``.

        :returns: A dict containing updated extra_specs
        """
        res = self._get_resource(_type.Type, type)
        extra_specs = res.set_extra_specs(self, **attrs)
        result = _type.Type.existing(id=res.id, extra_specs=extra_specs)
        return result

    def delete_type_extra_specs(self, type, keys):
        """Delete the extra_specs for a type

        Note: This method will do a HTTP DELETE request for every key in keys.

        :param type: The value can be either the ID of a type or a
            :class:`~openstack.block_storage.v3.type.Type` instance.
        :param keys: The keys to delete

        :returns: ``None``
        """
        res = self._get_resource(_type.Type, type)
        return res.delete_extra_specs(self, keys)

    def get_type_access(self, type):
        """Lists project IDs that have access to private volume type.

        :param type: The value can be either the ID of a type or a
            :class:`~openstack.block_storage.v3.type.Type` instance.

        :returns: List of dictionaries describing projects that have access to
            the specified type
        """
        res = self._get_resource(_type.Type, type)
        return res.get_private_access(self)

    def add_type_access(self, type, project_id):
        """Adds private volume type access to a project.

        :param type: The value can be either the ID of a type or a
            :class:`~openstack.block_storage.v3.type.Type` instance.
        :param str project_id: The ID of the project. Volume Type access to
            be added to this project ID.

        :returns: ``None``
        """
        res = self._get_resource(_type.Type, type)
        return res.add_private_access(self, project_id)

    def remove_type_access(self, type, project_id):
        """Remove private volume type access from a project.

        :param type: The value can be either the ID of a type or a
            :class:`~openstack.block_storage.v3.type.Type` instance.
        :param str project_id: The ID of the project. Volume Type access to
            be removed to this project ID.

        :returns: ``None``
        """
        res = self._get_resource(_type.Type, type)
        return res.remove_private_access(self, project_id)

    def get_type_encryption(self, volume_type_id):
        """Get the encryption details of a volume type

        :param volume_type_id: The value can be the ID of a type or a
            :class:`~openstack.block_storage.v3.type.Type`
            instance.

        :returns: One :class:`~openstack.block_storage.v3.type.TypeEncryption`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
            when no resource can be found.
        """
        volume_type = self._get_resource(_type.Type, volume_type_id)

        return self._get(_type.TypeEncryption,
                         volume_type_id=volume_type.id,
                         requires_id=False)

    def create_type_encryption(self, volume_type, **attrs):
        """Create new type encryption from attributes

        :param volume_type: The value can be the ID of a type or a
            :class:`~openstack.block_storage.v3.type.Type`
            instance.

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.block_storage.v3.type.TypeEncryption`,
            comprised of the properties on the TypeEncryption class.

        :returns: The results of type encryption creation
        :rtype: :class:`~openstack.block_storage.v3.type.TypeEncryption`
        """
        volume_type = self._get_resource(_type.Type, volume_type)

        return self._create(_type.TypeEncryption,
                            volume_type_id=volume_type.id, **attrs)

    def delete_type_encryption(self, encryption=None,
                               volume_type=None, ignore_missing=True):
        """Delete type encryption attributes

        :param encryption: The value can be None or a
            :class:`~openstack.block_storage.v3.type.TypeEncryption`
            instance.  If encryption_id is None then
            volume_type_id must be specified.

        :param volume_type: The value can be the ID of a type or a
            :class:`~openstack.block_storage.v3.type.Type`
            instance.  Required if encryption_id is None.

        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be
            raised when the type does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent type.

        :returns: ``None``
        """

        if volume_type:
            volume_type = self._get_resource(_type.Type, volume_type)
            encryption = self._get(_type.TypeEncryption,
                                   volume_type=volume_type.id,
                                   requires_id=False)

        self._delete(_type.TypeEncryption, encryption,
                     ignore_missing=ignore_missing)

    def update_type_encryption(self, encryption=None,
                               volume_type=None, **attrs):
        """Update a type
        :param encryption: The value can be None or a
            :class:`~openstack.block_storage.v3.type.TypeEncryption`
            instance.  If encryption_id is None then
            volume_type_id must be specified.

        :param volume_type: The value can be the ID of a type or a
            :class:`~openstack.block_storage.v3.type.Type`
            instance.  Required if encryption_id is None.
        :param dict attrs: The attributes to update on the type encryption.

        :returns: The updated type encryption
        :rtype: :class:`~openstack.block_storage.v3.type.TypeEncryption`
        """

        if volume_type:
            volume_type = self._get_resource(_type.Type, volume_type)
            encryption = self._get(_type.TypeEncryption,
                                   volume_type=volume_type.id,
                                   requires_id=False)

        return self._update(_type.TypeEncryption, encryption, **attrs)

    # ====== VOLUMES ======
    def get_volume(self, volume):
        """Get a single volume

        :param volume: The value can be the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.

        :returns: One :class:`~openstack.block_storage.v3.volume.Volume`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
            when no resource can be found.
        """
        return self._get(_volume.Volume, volume)

    def find_volume(self, name_or_id, ignore_missing=True, **attrs):
        """Find a single volume

        :param snapshot: The name or ID a volume
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the volume does not exist.

        :returns: One :class:`~openstack.block_storage.v3.volume.Volume`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
            when no resource can be found.
        """
        return self._find(_volume.Volume, name_or_id,
                          ignore_missing=ignore_missing)

    def volumes(self, details=True, **query):
        """Retrieve a generator of volumes

        :param bool details: When set to ``False`` no extended attributes
            will be returned. The default, ``True``, will cause objects with
            additional attributes to be returned.
        :param kwargs query: Optional query parameters to be sent to limit
            the volumes being returned.  Available parameters include:

            * name: Name of the volume as a string.
            * all_projects: Whether return the volumes in all projects
            * status: Value of the status of the volume so that you can filter
              on "available" for example.

        :returns: A generator of volume objects.
        """
        base_path = '/volumes/detail' if details else None
        return self._list(_volume.Volume, base_path=base_path, **query)

    def create_volume(self, **attrs):
        """Create a new volume from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.block_storage.v3.volume.Volume`,
            comprised of the properties on the Volume class.

        :returns: The results of volume creation
        :rtype: :class:`~openstack.block_storage.v3.volume.Volume`
        """
        return self._create(_volume.Volume, **attrs)

    def delete_volume(self, volume, ignore_missing=True, force=False):
        """Delete a volume

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be
            raised when the volume does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent volume.
        :param bool force: Whether to try forcing volume deletion.

        :returns: ``None``
        """
        if not force:
            self._delete(_volume.Volume, volume, ignore_missing=ignore_missing)
        else:
            volume = self._get_resource(_volume.Volume, volume)
            volume.force_delete(self)

    # ====== VOLUME ACTIONS ======
    def extend_volume(self, volume, size):
        """Extend a volume

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.
        :param size: New volume size

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.extend(self, size)

    def set_volume_readonly(self, volume, readonly=True):
        """Set a volume's read-only flag.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.
        :param bool readonly: Whether the volume should be a read-only volume
            or not.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.set_readonly(self, readonly)

    def retype_volume(self, volume, new_type, migration_policy="never"):
        """Retype the volume.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.
        :param str new_type: The new volume type that volume is changed with.
        :param str migration_policy: Specify if the volume should be migrated
            when it is re-typed. Possible values are on-demand or never.
            Default: never.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.retype(self, new_type, migration_policy)

    def set_volume_bootable_status(self, volume, bootable):
        """Set bootable status of the volume.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.
        :param bool bootable: Specifies whether the volume should be bootable
            or not.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.set_bootable_status(self, bootable)

    def reset_volume_status(
        self, volume, status, attach_status, migration_status
    ):
        """Reset volume statuses.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.
        :param str status: The new volume status.
        :param str attach_status: The new volume attach status.
        :param str migration_status: The new volume migration status (admin
            only).

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.reset_status(self, status, attach_status, migration_status)

    def revert_volume_to_snapshot(
        self, volume, snapshot
    ):
        """Revert a volume to its latest snapshot.

        This method only support reverting a detached volume, and the
        volume status must be available.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.
        :param snapshot:  The value can be either the ID of a snapshot or a
            :class:`~openstack.block_storage.v3.snapshot.Snapshot` instance.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        snapshot = self._get_resource(_snapshot.Snapshot, snapshot)
        volume.revert_to_snapshot(self, snapshot.id)

    def attach_volume(
        self, volume, mountpoint, instance=None, host_name=None
    ):
        """Attaches a volume to a server.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.
        :param str mountpoint: The attaching mount point.
        :param str instance: The UUID of the attaching instance.
        :param str host_name: The name of the attaching host.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.attach(self, mountpoint, instance, host_name)

    def detach_volume(
        self, volume, attachment, force=False, connector=None
    ):
        """Detaches a volume from a server.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.
        :param str attachment: The ID of the attachment.
        :param bool force: Whether to force volume detach (Rolls back an
            unsuccessful detach operation after you disconnect the volume.)
        :param dict connector: The connector object.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.detach(self, attachment, force, connector)

    def unmanage_volume(self, volume):
        """Removes a volume from Block Storage management without removing the
            back-end storage object that is associated with it.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.

        :returns: None """
        volume = self._get_resource(_volume.Volume, volume)
        volume.unmanage(self)

    def migrate_volume(
        self, volume, host=None, force_host_copy=False,
        lock_volume=False, cluster=None
    ):
        """Migrates a volume to the specified host.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.
        :param str host: The target host for the volume migration. Host
            format is host@backend.
        :param bool force_host_copy: If false (the default), rely on the volume
            backend driver to perform the migration, which might be optimized.
            If true, or the volume driver fails to migrate the volume itself,
            a generic host-based migration is performed.
        :param bool lock_volume: If true, migrating an available volume will
            change its status to maintenance preventing other operations from
            being performed on the volume such as attach, detach, retype, etc.
        :param str cluster: The target cluster for the volume migration.
            Cluster format is cluster@backend. Starting with microversion
            3.16, either cluster or host must be specified. If host is
            specified and is part of a cluster, the cluster is used as the
            target for the migration.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.migrate(self, host, force_host_copy, lock_volume, cluster)

    def complete_volume_migration(
        self, volume, new_volume, error=False
    ):
        """Complete the migration of a volume.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.
        :param str new_volume: The UUID of the new volume.
        :param bool error: Used to indicate if an error has occured elsewhere
            that requires clean up.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.complete_migration(self, new_volume, error)

    def upload_volume_to_image(
        self, volume, image_name, force=False, disk_format=None,
        container_format=None, visibility=None, protected=None
    ):
        """Uploads the specified volume to image service.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.
        :param str image name: The name for the new image.
        :param bool force: Enables or disables upload of a volume that is
            attached to an instance.
        :param str disk_format: Disk format for the new image.
        :param str container_format: Container format for the new image.
        :param str visibility: The visibility property of the new image.
        :param str protected: Whether the new image is protected.

        :returns: dictionary describing the image.
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.upload_to_image(
            self, image_name, force=force, disk_format=disk_format,
            container_format=container_format, visibility=visibility,
            protected=protected
        )

    def reserve_volume(self, volume):
        """Mark volume as reserved.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.

        :returns: None """
        volume = self._get_resource(_volume.Volume, volume)
        volume.reserve(self)

    def unreserve_volume(self, volume):
        """Unmark volume as reserved.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.

        :returns: None """
        volume = self._get_resource(_volume.Volume, volume)
        volume.unreserve(self)

    def begin_volume_detaching(self, volume):
        """Update volume status to 'detaching'.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.

        :returns: None """
        volume = self._get_resource(_volume.Volume, volume)
        volume.begin_detaching(self)

    def abort_volume_detaching(self, volume):
        """Update volume status to 'in-use'.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.

        :returns: None """
        volume = self._get_resource(_volume.Volume, volume)
        volume.abort_detaching(self)

    def init_volume_attachment(self, volume, connector):
        """Initialize volume attachment.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.
        :param dict connector: The connector object.

        :returns: None """
        volume = self._get_resource(_volume.Volume, volume)
        volume.init_attachment(self, connector)

    def terminate_volume_attachment(self, volume, connector):
        """Update volume status to 'in-use'.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.
        :param dict connector: The connector object.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.terminate_attachment(self, connector)

    # ====== BACKEND POOLS ======
    def backend_pools(self, **query):
        """Returns a generator of cinder Back-end storage pools

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns A generator of cinder Back-end storage pools objects
        """
        return self._list(_stats.Pools, **query)

    # ====== BACKUPS ======
    def backups(self, details=True, **query):
        """Retrieve a generator of backups

        :param bool details: When set to ``False``
            no additional details will be returned. The default, ``True``,
            will cause objects with additional attributes to be returned.
        :param dict query: Optional query parameters to be sent to limit the
            resources being returned:

            * offset: pagination marker
            * limit: pagination limit
            * sort_key: Sorts by an attribute. A valid value is
              name, status, container_format, disk_format, size, id,
              created_at, or updated_at. Default is created_at.
              The API uses the natural sorting direction of the
              sort_key attribute value.
            * sort_dir: Sorts by one or more sets of attribute and sort
              direction combinations. If you omit the sort direction
              in a set, default is desc.
            * project_id: Project ID to query backups for.

        :returns: A generator of backup objects.
        """
        base_path = '/backups/detail' if details else None
        return self._list(_backup.Backup, base_path=base_path, **query)

    def get_backup(self, backup):
        """Get a backup

        :param backup: The value can be the ID of a backup
            or a :class:`~openstack.block_storage.v3.backup.Backup`
            instance.

        :returns: Backup instance
        :rtype: :class:`~openstack.block_storage.v3.backup.Backup`
        """
        return self._get(_backup.Backup, backup)

    def find_backup(self, name_or_id, ignore_missing=True, **attrs):
        """Find a single backup

        :param snapshot: The name or ID a backup
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the backup does not exist.

        :returns: One :class:`~openstack.block_storage.v3.backup.Backup`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
            when no resource can be found.
        """
        return self._find(_backup.Backup, name_or_id,
                          ignore_missing=ignore_missing)

    def create_backup(self, **attrs):
        """Create a new Backup from attributes with native API

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.block_storage.v3.backup.Backup`
            comprised of the properties on the Backup class.

        :returns: The results of Backup creation
        :rtype: :class:`~openstack.block_storage.v3.backup.Backup`
        """
        return self._create(_backup.Backup, **attrs)

    def delete_backup(self, backup, ignore_missing=True, force=False):
        """Delete a CloudBackup

        :param backup: The value can be the ID of a backup or a
            :class:`~openstack.block_storage.v3.backup.Backup` instance
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the zone does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent zone.
        :param bool force: Whether to try forcing backup deletion

        :returns: ``None``
        """
        if not force:
            self._delete(
                _backup.Backup, backup, ignore_missing=ignore_missing)
        else:
            backup = self._get_resource(_backup.Backup, backup)
            backup.force_delete(self)

    # ====== BACKUP ACTIONS ======
    def restore_backup(self, backup, volume_id=None, name=None):
        """Restore a Backup to volume

        :param backup: The value can be the ID of a backup or a
            :class:`~openstack.block_storage.v3.backup.Backup` instance
        :param volume_id: The ID of the volume to restore the backup to.
        :param name: The name for new volume creation to restore.

        :returns: Updated backup instance
        :rtype: :class:`~openstack.block_storage.v3.backup.Backup`
        """
        backup = self._get_resource(_backup.Backup, backup)
        return backup.restore(self, volume_id=volume_id, name=name)

    def reset_backup(self, backup, status):
        """Reset status of the backup

        :param backup: The value can be either the ID of a backup or a
            :class:`~openstack.block_storage.v3.backup.Backup` instance.
        :param str status: New backup status

        :returns: None
        """
        backup = self._get_resource(_backup.Backup, backup)
        backup.reset(self, status)

    # ====== LIMITS ======
    def get_limits(self):
        """Retrieves limits

        :returns: A Limit object, including both
            :class:`~openstack.block_storage.v3.limits.AbsoluteLimit` and
            :class:`~openstack.block_storage.v3.limits.RateLimit`
        :rtype: :class:`~openstack.block_storage.v3.limits.Limit`
        """
        return self._get(_limits.Limit, requires_id=False)

    def get_capabilities(self, host):
        """Get a backend's capabilites

        :param host: Specified backend to obtain volume stats and properties.

        :returns: One :class:
            `~openstack.block_storage.v3.capabilites.Capabilities` instance.
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            resource can be found.
        """
        return self._get(_capabilities.Capabilities, host)

    def availability_zones(self):
        """Return a generator of availability zones

        :returns: A generator of availability zone
        :rtype:
            :class:`~openstack.block_storage.v3.availability_zone.AvailabilityZone`
        """

        return self._list(availability_zone.AvailabilityZone)

    def get_group_type(self, group_type):
        """Get a specific group type

        :param group_type: The value can be the ID of a group type
            or a :class:`~openstack.block_storage.v3.group_type.GroupType`
            instance.

        :returns: One :class:
            `~openstack.block_storage.v3.group_type.GroupType` instance.
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            resource can be found.
        """
        return self._get(_group_type.GroupType, group_type)

    def find_group_type(self, name_or_id, ignore_missing=True):
        """Find a single group type

        :param name_or_id: The name or ID of a group type.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the group type does not exist.

        :returns: One
            :class:`~openstack.block_storage.v3.group_type.GroupType`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            resource can be found.
        """
        return self._find(
            _group_type.GroupType, name_or_id, ignore_missing=ignore_missing)

    def group_types(self, **query):
        """Retrive a generator of group types

        :param dict query: Optional query parameters to be sent to limit the
            resources being returned:

            * sort: Comma-separated list of sort keys and optional sort
              directions in the form of <key> [:<direction>]. A valid
              direction is asc (ascending) or desc (descending).
            * limit: Requests a page size of items. Returns a number of items
              up to a limit value. Use the limit parameter to make an
              initial limited request and use the ID of the last-seen item
              from the response as the marker parameter value in a
              subsequent limited request.
            * offset: Used in conjunction with limit to return a slice of
              items. Is where to start in the list.
            * marker: The ID of the last-seen item.

        :returns: A generator of group type objects.
        """
        return self._list(_group_type.GroupType, **query)

    def create_group_type(self, **attrs):
        """Create a group type

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.block_storage.v3.group_type.GroupType`
            comprised of the properties on the GroupType class.

        :returns: The results of group type creation.
        :rtype: :class:`~openstack.block_storage.v3.group_type.GroupTye`.
        """
        return self._create(_group_type.GroupType, **attrs)

    def delete_group_type(self, group_type, ignore_missing=True):
        """Delete a group type

        :param group_type: The value can be the ID of a group type
            or a :class:`~openstack.block_storage.v3.group_type.GroupType`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the zone does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent zone.

        :returns: ''None''
        """
        self._delete(
            _group_type.GroupType, group_type, ignore_missing=ignore_missing)

    def update_group_type(self, group_type, **attrs):
        """Update a group_type

        :param group_type: The value can be the ID of a group type or a
            :class:`~openstack.block_storage.v3.group_type.GroupType`
            instance.
        :param dict attrs: The attributes to update on the group type.

        :returns: The updated group type.
        :rtype: :class:`~openstack.block_storage.v3.group_type.GroupType`
        """
        return self._update(
            _group_type.GroupType, group_type, **attrs)

    def wait_for_status(self, res, status='available', failures=None,
                        interval=2, wait=120):
        """Wait for a resource to be in a particular status.

        :param res: The resource to wait on to reach the specified status.
            The resource must have a ``status`` attribute.
        :type resource: A :class:`~openstack.resource.Resource` object.
        :param status: Desired status.
        :param failures: Statuses that would be interpreted as failures.
        :type failures: :py:class:`list`
        :param interval: Number of seconds to wait before to consecutive
            checks. Default to 2.
        :param wait: Maximum number of seconds to wait before the change.
            Default to 120.
        :returns: The resource is returned on success.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if transition
            to the desired status failed to occur in specified seconds.
        :raises: :class:`~openstack.exceptions.ResourceFailure` if the resource
            has transited to one of the failure statuses.
        :raises: :class:`~AttributeError` if the resource does not have a
            ``status`` attribute.
        """
        failures = ['error'] if failures is None else failures
        return resource.wait_for_status(
            self, res, status, failures, interval, wait)

    def wait_for_delete(self, res, interval=2, wait=120):
        """Wait for a resource to be deleted.

        :param res: The resource to wait on to be deleted.
        :type resource: A :class:`~openstack.resource.Resource` object.
        :param interval: Number of seconds to wait before to consecutive
            checks. Default to 2.
        :param wait: Maximum number of seconds to wait before the change.
            Default to 120.
        :returns: The resource is returned on success.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if transition
            to delete failed to occur in the specified seconds.
        """
        return resource.wait_for_delete(self, res, interval, wait)

    def resource_filters(self, **query):
        """Retrieve a generator of resource filters

        :returns: A generator of resource filters.
        """
        return self._list(_resource_filter.ResourceFilter, **query)

    def extensions(self):
        """Return a generator of extensions

        :returns: A generator of extension
        :rtype: :class:`~openstack.block_storage.v3.extension.Extension`
        """
        return self._list(_extension.Extension)

    def get_quota_set(self, project, usage=False, **query):
        """Show QuotaSet information for the project

        :param project: ID or instance of
            :class:`~openstack.identity.project.Project` of the project for
            which the quota should be retrieved
        :param bool usage: When set to ``True`` quota usage and reservations
            would be filled.
        :param dict query: Additional query parameters to use.

        :returns: One :class:`~openstack.block_storage.v3.quota_set.QuotaSet`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
            when no resource can be found.
        """
        project = self._get_resource(_project.Project, project)
        res = self._get_resource(
            _quota_set.QuotaSet, None, project_id=project.id)
        return res.fetch(
            self, usage=usage, **query)

    def get_quota_set_defaults(self, project):
        """Show QuotaSet defaults for the project

        :param project: ID or instance of
            :class:`~openstack.identity.project.Project` of the project for
            which the quota should be retrieved

        :returns: One :class:`~openstack.block_storage.v3.quota_set.QuotaSet`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
            when no resource can be found.
        """
        project = self._get_resource(_project.Project, project)
        res = self._get_resource(
            _quota_set.QuotaSet, None, project_id=project.id)
        return res.fetch(
            self, base_path='/os-quota-sets/defaults')

    def revert_quota_set(self, project, **query):
        """Reset Quota for the project/user.

        :param project: ID or instance of
            :class:`~openstack.identity.project.Project` of the project for
            which the quota should be resetted.
        :param dict query: Additional parameters to be used.

        :returns: ``None``
        """
        project = self._get_resource(_project.Project, project)
        res = self._get_resource(
            _quota_set.QuotaSet, None, project_id=project.id)

        if not query:
            query = {}
        return res.delete(self, **query)

    def update_quota_set(self, quota_set, query=None, **attrs):
        """Update a QuotaSet.

        :param quota_set: Either the ID of a quota_set or a
            :class:`~openstack.block_storage.v3.quota_set.QuotaSet` instance.
        :param dict query: Optional parameters to be used with update call.
        :attrs kwargs: The attributes to update on the QuotaSet represented
            by ``quota_set``.

        :returns: The updated QuotaSet
        :rtype: :class:`~openstack.block_storage.v3.quota_set.QuotaSet`
        """
        res = self._get_resource(_quota_set.QuotaSet, quota_set, **attrs)
        if not query:
            query = {}
        return res.commit(self, **query)

    def _get_cleanup_dependencies(self):
        return {
            'block_storage': {
                'before': []
            }
        }

    def _service_cleanup(self, dry_run=True, client_status_queue=None,
                         identified_resources=None,
                         filters=None, resource_evaluation_fn=None):
        backups = []
        for obj in self.backups(details=False):
            need_delete = self._service_cleanup_del_res(
                self.delete_backup,
                obj,
                dry_run=dry_run,
                client_status_queue=client_status_queue,
                identified_resources=identified_resources,
                filters=filters,
                resource_evaluation_fn=resource_evaluation_fn)
            if not dry_run and need_delete:
                backups.append(obj)

        # Before deleting snapshots need to wait for backups to be deleted
        for obj in backups:
            try:
                self.wait_for_delete(obj)
            except exceptions.SDKException:
                # Well, did our best, still try further
                pass

        snapshots = []
        for obj in self.snapshots(details=False):
            need_delete = self._service_cleanup_del_res(
                self.delete_snapshot,
                obj,
                dry_run=dry_run,
                client_status_queue=client_status_queue,
                identified_resources=identified_resources,
                filters=filters,
                resource_evaluation_fn=resource_evaluation_fn)
            if not dry_run and need_delete:
                snapshots.append(obj)

        # Before deleting volumes need to wait for snapshots to be deleted
        for obj in snapshots:
            try:
                self.wait_for_delete(obj)
            except exceptions.SDKException:
                # Well, did our best, still try further
                pass

        for obj in self.volumes(details=True):
            self._service_cleanup_del_res(
                self.delete_volume,
                obj,
                dry_run=dry_run,
                client_status_queue=client_status_queue,
                identified_resources=identified_resources,
                filters=filters,
                resource_evaluation_fn=resource_evaluation_fn)

    def get_volume_metadata(self, volume):
        """Return a dictionary of metadata for a volume

        :param volume: Either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume`.

        :returns: A :class:`~openstack.block_storage.v3.volume.Volume` with the
            volume's metadata. All keys and values are Unicode text.
        :rtype: :class:`~openstack.block_storage.v3.volume.Volume`
        """
        volume = self._get_resource(_volume.Volume, volume)
        return volume.fetch_metadata(self)

    def set_volume_metadata(self, volume, **metadata):
        """Update metadata for a volume

        :param volume: Either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume`.
        :param kwargs metadata: Key/value pairs to be updated in the volume's
            metadata. No other metadata is modified by this call. All keys
            and values are stored as Unicode.

        :returns: A :class:`~openstack.block_storage.v3.volume.Volume` with the
            volume's metadata. All keys and values are Unicode text.
        :rtype: :class:`~openstack.block_storage.v3.volume.Volume`
        """
        volume = self._get_resource(_volume.Volume, volume)
        return volume.set_metadata(self, metadata=metadata)

    def delete_volume_metadata(self, volume, keys=None):
        """Delete metadata for a volume

        :param volume: Either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume`.
        :param list keys: The keys to delete. If left empty complete
            metadata will be removed.

        :rtype: ``None``
        """
        volume = self._get_resource(_volume.Volume, volume)
        if keys is not None:
            for key in keys:
                volume.delete_metadata_item(self, key)
        else:
            volume.delete_metadata(self)

    def get_snapshot_metadata(self, snapshot):
        """Return a dictionary of metadata for a snapshot

        :param snapshot: Either the ID of a snapshot or a
            :class:`~openstack.block_storage.v3.snapshot.Snapshot`.

        :returns: A
            :class:`~openstack.block_storage.v3.snapshot.Snapshot` with the
            snapshot's metadata. All keys and values are Unicode text.
        :rtype: :class:`~openstack.block_storage.v3.snapshot.Snapshot`
        """
        snapshot = self._get_resource(_snapshot.Snapshot, snapshot)
        return snapshot.fetch_metadata(self)

    def set_snapshot_metadata(self, snapshot, **metadata):
        """Update metadata for a snapshot

        :param snapshot: Either the ID of a snapshot or a
            :class:`~openstack.block_storage.v3.snapshot.Snapshot`.
        :param kwargs metadata: Key/value pairs to be updated in the snapshot's
            metadata. No other metadata is modified by this call. All keys
            and values are stored as Unicode.

        :returns: A
            :class:`~openstack.block_storage.v3.snapshot.Snapshot` with the
            snapshot's metadata. All keys and values are Unicode text.
        :rtype: :class:`~openstack.block_storage.v3.snapshot.Snapshot`
        """
        snapshot = self._get_resource(_snapshot.Snapshot, snapshot)
        return snapshot.set_metadata(self, metadata=metadata)

    def delete_snapshot_metadata(self, snapshot, keys=None):
        """Delete metadata for a snapshot

        :param snapshot: Either the ID of a snapshot or a
            :class:`~openstack.block_storage.v3.snapshot.Snapshot`.
        :param list keys: The keys to delete. If left empty complete
            metadata will be removed.

        :rtype: ``None``
        """
        snapshot = self._get_resource(_snapshot.Snapshot, snapshot)
        if keys is not None:
            for key in keys:
                snapshot.delete_metadata_item(self, key)
        else:
            snapshot.delete_metadata(self)
