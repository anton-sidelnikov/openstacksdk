# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# import types so that we can reference ListType in sphinx param declarations.
# We can't just use list, because sphinx gets confused by
# openstack.resource.Resource.list and openstack.resource2.Resource.list
import types  # noqa

from openstack.block_storage.v3 import quota_set as _qs
from openstack.cloud import _utils
from openstack.cloud import exc
from openstack import exceptions
from openstack import proxy


def _no_pending_volumes(volumes):
    """If there are any volumes not in a steady state, don't cache"""
    for volume in volumes:
        if volume['status'] not in ('available', 'error', 'in-use'):
            return False
    return True


class BlockStorageCloudMixin:

    @_utils.cache_on_arguments(should_cache_fn=_no_pending_volumes)
    def list_volumes(self, cache=True):
        """List all available volumes.

        :returns: A list of volume ``munch.Munch``.

        """
        return list(self.block_storage.volumes())

    @_utils.cache_on_arguments()
    def list_volume_types(self, get_extra=True):
        """List all available volume types.

        :returns: A list of volume ``munch.Munch``.

        """
        return list(self.block_storage.types())

    def get_volume(self, name_or_id, filters=None):
        """Get a volume by name or ID.

        :param name_or_id: Name or ID of the volume.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'last_name': 'Smith',
                  'other': {
                      'gender': 'Female'
                  }
                }

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A volume ``munch.Munch`` or None if no matching volume is
                  found.

        """
        return _utils._get_entity(self, 'volume', name_or_id, filters)

    def get_volume_by_id(self, id):
        """ Get a volume by ID

        :param id: ID of the volume.
        :returns: A volume ``munch.Munch``.
        """
        return self.block_storage.get_volume(id)

    def get_volume_type(self, name_or_id, filters=None):
        """Get a volume type by name or ID.

        :param name_or_id: Name or ID of the volume.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'last_name': 'Smith',
                  'other': {
                      'gender': 'Female'
                  }
                }

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A volume ``munch.Munch`` or None if no matching volume is
                  found.

        """
        return _utils._get_entity(
            self, 'volume_type', name_or_id, filters)

    def create_volume(
            self, size,
            wait=True, timeout=None, image=None, bootable=None, **kwargs):
        """Create a volume.

        :param size: Size, in GB of the volume to create.
        :param name: (optional) Name for the volume.
        :param description: (optional) Name for the volume.
        :param wait: If true, waits for volume to be created.
        :param timeout: Seconds to wait for volume creation. None is forever.
        :param image: (optional) Image name, ID or object from which to create
                      the volume
        :param bootable: (optional) Make this volume bootable. If set, wait
                         will also be set to true.
        :param kwargs: Keyword arguments as expected for cinder client.

        :returns: The created volume object.

        :raises: OpenStackCloudTimeout if wait time exceeded.
        :raises: OpenStackCloudException on operation error.
        """
        if bootable is not None:
            wait = True

        if image:
            image_obj = self.get_image(image)
            if not image_obj:
                raise exc.OpenStackCloudException(
                    "Image {image} was requested as the basis for a new"
                    " volume, but was not found on the cloud".format(
                        image=image))
            kwargs['imageRef'] = image_obj['id']
        kwargs = self._get_volume_kwargs(kwargs)
        kwargs['size'] = size

        volume = self.block_storage.create_volume(**kwargs)

        self.list_volumes.invalidate(self)

        if volume['status'] == 'error':
            raise exc.OpenStackCloudException("Error in creating volume")

        if wait:
            self.block_storage.wait_for_status(volume, wait=timeout)
            if bootable:
                self.block_storage.set_volume_bootable_status(volume, True)

        return volume

    def update_volume(self, name_or_id, **kwargs):
        kwargs = self._get_volume_kwargs(kwargs)

        volume = self.get_volume(name_or_id)
        if not volume:
            raise exc.OpenStackCloudException(
                "Volume %s not found." % name_or_id)

        volume = self.block_storage.update_volume(
            volume, **kwargs)

        self.list_volumes.invalidate(self)

        return volume

    def set_volume_bootable(self, name_or_id, bootable=True):
        """Set a volume's bootable flag.

        :param name_or_id: Name, unique ID of the volume or a volume dict.
        :param bool bootable: Whether the volume should be bootable.
                              (Defaults to True)

        :raises: OpenStackCloudTimeout if wait time exceeded.
        :raises: OpenStackCloudException on operation error.
        """

        volume = self.get_volume(name_or_id)

        if not volume:
            raise exc.OpenStackCloudException(
                "Volume {name_or_id} does not exist".format(
                    name_or_id=name_or_id))

        return self.block_storage.set_volume_bootable_status(volume, bootable)

    def delete_volume(self, name_or_id=None, wait=True, timeout=None,
                      force=False):
        """Delete a volume.

        :param name_or_id: Name or unique ID of the volume.
        :param wait: If true, waits for volume to be deleted.
        :param timeout: Seconds to wait for volume deletion. None is forever.
        :param force: Force delete volume even if the volume is in deleting
            or error_deleting state.

        :raises: OpenStackCloudTimeout if wait time exceeded.
        :raises: OpenStackCloudException on operation error.
        """

        self.list_volumes.invalidate(self)
        volume = self.block_storage.find_volume(name_or_id)

        if not volume:
            self.log.debug(
                "Volume %(name_or_id)s does not exist",
                {'name_or_id': name_or_id},
                exc_info=True)
            return False
        try:
            self.block_storage.delete_volume(volume, force=force)
        except exceptions.SDKException:
            self.log.exception("error in deleting volume")
            raise

        self.list_volumes.invalidate(self)
        if wait:
            self.block_storage.wait_for_delete(volume, wait=timeout)

        return True

    def get_volumes(self, server, cache=True):
        volumes = []
        for volume in self.list_volumes(cache=cache):
            for attach in volume['attachments']:
                if attach['server_id'] == server['id']:
                    volumes.append(volume)
        return volumes

    def get_volume_limits(self, name_or_id=None):
        """ Get volume limits for a project

        :param name_or_id: (optional) project name or ID to get limits for
                           if different from the current project
        :raises: OpenStackCloudException if it's not a valid project

        :returns: Munch object with the limits
        """
        params = {}
        project_id = None
        error_msg = "Failed to get limits"
        if name_or_id:

            proj = self.get_project(name_or_id)
            if not proj:
                raise exc.OpenStackCloudException("project does not exist")
            project_id = proj.id
            params['tenant_id'] = project_id
            error_msg = "{msg} for the project: {project} ".format(
                msg=error_msg, project=name_or_id)

        data = proxy._json_response(
            self.block_storage.get('/limits', params=params))
        limits = self._get_and_munchify('limits', data)
        return limits

    def get_volume_id(self, name_or_id):
        volume = self.get_volume(name_or_id)
        if volume:
            return volume['id']
        return None

    def volume_exists(self, name_or_id):
        return self.get_volume(name_or_id) is not None

    def get_volume_attach_device(self, volume, server_id):
        """Return the device name a volume is attached to for a server.

        This can also be used to verify if a volume is attached to
        a particular server.

        :param volume: Volume dict
        :param server_id: ID of server to check

        :returns: Device name if attached, None if volume is not attached.
        """
        for attach in volume['attachments']:
            if server_id == attach['server_id']:
                return attach['device']
        return None

    def detach_volume(self, server, volume, wait=True, timeout=None):
        """Detach a volume from a server.

        :param server: The server dict to detach from.
        :param volume: The volume dict to detach.
        :param wait: If true, waits for volume to be detached.
        :param timeout: Seconds to wait for volume detachment. None is forever.

        :raises: OpenStackCloudTimeout if wait time exceeded.
        :raises: OpenStackCloudException on operation error.
        """
        self.compute.delete_volume_attachment(
            volume['id'], server['id'],
            ignore_missing=False)

        if wait:
            vol = self.get_volume(volume['id'])
            self.block_storage.wait_for_status(vol)

    def attach_volume(self, server, volume, device=None,
                      wait=True, timeout=None):
        """Attach a volume to a server.

        This will attach a volume, described by the passed in volume
        dict (as returned by get_volume()), to the server described by
        the passed in server dict (as returned by get_server()) on the
        named device on the server.

        If the volume is already attached to the server, or generally not
        available, then an exception is raised. To re-attach to a server,
        but under a different device, the user must detach it first.

        :param server: The server dict to attach to.
        :param volume: The volume dict to attach.
        :param device: The device name where the volume will attach.
        :param wait: If true, waits for volume to be attached.
        :param timeout: Seconds to wait for volume attachment. None is forever.

        :returns: a volume attachment object.

        :raises: OpenStackCloudTimeout if wait time exceeded.
        :raises: OpenStackCloudException on operation error.
        """
        dev = self.get_volume_attach_device(volume, server['id'])
        if dev:
            raise exc.OpenStackCloudException(
                "Volume %s already attached to server %s on device %s"
                % (volume['id'], server['id'], dev)
            )

        if volume['status'] != 'available':
            raise exc.OpenStackCloudException(
                "Volume %s is not available. Status is '%s'"
                % (volume['id'], volume['status'])
            )

        payload = {'volumeId': volume['id']}
        if device:
            payload['device'] = device
        attachment = self.compute.create_volume_attachment(
            server=server['id'], **payload)

        if wait:
            if not hasattr(volume, 'fetch'):
                # If we got volume as dict we need to re-fetch it to be able to
                # use wait_for_status.
                volume = self.block_storage.get_volume(volume['id'])
            self.block_storage.wait_for_status(
                volume, 'in-use', wait=timeout)
        return attachment

    def _get_volume_kwargs(self, kwargs):
        name = kwargs.pop('name', kwargs.pop('display_name', None))
        description = kwargs.pop('description',
                                 kwargs.pop('display_description', None))
        if name:
            kwargs['name'] = name
        if description:
            kwargs['description'] = description
        return kwargs

    @_utils.valid_kwargs('name', 'display_name',
                         'description', 'display_description')
    def create_volume_snapshot(self, volume_id, force=False,
                               wait=True, timeout=None, **kwargs):
        """Create a volume.

        :param volume_id: the ID of the volume to snapshot.
        :param force: If set to True the snapshot will be created even if the
                      volume is attached to an instance, if False it will not
        :param name: name of the snapshot, one will be generated if one is
                     not provided
        :param description: description of the snapshot, one will be generated
                            if one is not provided
        :param wait: If true, waits for volume snapshot to be created.
        :param timeout: Seconds to wait for volume snapshot creation. None is
                        forever.

        :returns: The created volume object.

        :raises: OpenStackCloudTimeout if wait time exceeded.
        :raises: OpenStackCloudException on operation error.
        """

        kwargs = self._get_volume_kwargs(kwargs)
        payload = {'volume_id': volume_id}
        payload.update(kwargs)
        snapshot = self.block_storage.create_snapshot(**payload)
        if wait:
            snapshot = self.block_storage.wait_for_status(
                snapshot, wait=timeout)

        return snapshot

    def get_volume_snapshot_by_id(self, snapshot_id):
        """Takes a snapshot_id and gets a dict of the snapshot
        that maches that ID.

        Note: This is more efficient than get_volume_snapshot.

        param: snapshot_id: ID of the volume snapshot.

        """
        return self.block_storage.get_snapshot(snapshot_id)

    def get_volume_snapshot(self, name_or_id, filters=None):
        """Get a volume by name or ID.

        :param name_or_id: Name or ID of the volume snapshot.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'last_name': 'Smith',
                  'other': {
                      'gender': 'Female'
                  }
                }

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A volume ``munch.Munch`` or None if no matching volume is
                  found.
        """
        return _utils._get_entity(self, 'volume_snapshot', name_or_id,
                                  filters)

    def create_volume_backup(self, volume_id, name=None, description=None,
                             force=False, wait=True, timeout=None,
                             incremental=False, snapshot_id=None):

        """Create a volume backup.

        :param volume_id: the ID of the volume to backup.
        :param name: name of the backup, one will be generated if one is
                     not provided
        :param description: description of the backup, one will be generated
                            if one is not provided
        :param force: If set to True the backup will be created even if the
                      volume is attached to an instance, if False it will not
        :param wait: If true, waits for volume backup to be created.
        :param timeout: Seconds to wait for volume backup creation. None is
                        forever.
        :param incremental: If set to true, the backup will be incremental.
        :param snapshot_id: The UUID of the source snapshot to back up.

        :returns: The created volume backup object.

        :raises: OpenStackCloudTimeout if wait time exceeded.
        :raises: OpenStackCloudException on operation error.
        """
        payload = {
            'name': name,
            'volume_id': volume_id,
            'description': description,
            'force': force,
            'is_incremental': incremental,
            'snapshot_id': snapshot_id,
        }

        backup = self.block_storage.create_backup(**payload)

        if wait:
            backup = self.block_storage.wait_for_status(backup, wait=timeout)

        return backup

    def get_volume_backup(self, name_or_id, filters=None):
        """Get a volume backup by name or ID.

        :returns: A backup ``munch.Munch`` or None if no matching backup is
                  found.
        """
        return _utils._get_entity(self, 'volume_backup', name_or_id,
                                  filters)

    def list_volume_snapshots(self, detailed=True, search_opts=None):
        """List all volume snapshots.

        :returns: A list of volume snapshots ``munch.Munch``.

        """
        if not search_opts:
            search_opts = {}
        return list(self.block_storage.snapshots(
            details=detailed, **search_opts))

    def list_volume_backups(self, detailed=True, search_opts=None):
        """
        List all volume backups.

        :param bool detailed: Also list details for each entry
        :param dict search_opts: Search options
            A dictionary of meta data to use for further filtering. Example::

                {
                    'name': 'my-volume-backup',
                    'status': 'available',
                    'volume_id': 'e126044c-7b4c-43be-a32a-c9cbbc9ddb56',
                    'all_tenants': 1
                }

        :returns: A list of volume backups ``munch.Munch``.
        """
        if not search_opts:
            search_opts = {}

        return list(self.block_storage.backups(details=detailed,
                                               **search_opts))

    def delete_volume_backup(self, name_or_id=None, force=False, wait=False,
                             timeout=None):
        """Delete a volume backup.

        :param name_or_id: Name or unique ID of the volume backup.
        :param force: Allow delete in state other than error or available.
        :param wait: If true, waits for volume backup to be deleted.
        :param timeout: Seconds to wait for volume backup deletion. None is
                        forever.

        :raises: OpenStackCloudTimeout if wait time exceeded.
        :raises: OpenStackCloudException on operation error.
        """

        volume_backup = self.get_volume_backup(name_or_id)

        if not volume_backup:
            return False

        self.block_storage.delete_backup(
            volume_backup, ignore_missing=False, force=force)
        if wait:
            self.block_storage.wait_for_delete(volume_backup, wait=timeout)

        return True

    def delete_volume_snapshot(self, name_or_id=None, wait=False,
                               timeout=None):
        """Delete a volume snapshot.

        :param name_or_id: Name or unique ID of the volume snapshot.
        :param wait: If true, waits for volume snapshot to be deleted.
        :param timeout: Seconds to wait for volume snapshot deletion. None is
                        forever.

        :raises: OpenStackCloudTimeout if wait time exceeded.
        :raises: OpenStackCloudException on operation error.
        """

        volumesnapshot = self.get_volume_snapshot(name_or_id)

        if not volumesnapshot:
            return False

        self.block_storage.delete_snapshot(
            volumesnapshot, ignore_missing=False)

        if wait:
            self.block_storage.wait_for_delete(volumesnapshot, wait=timeout)

        return True

    def search_volumes(self, name_or_id=None, filters=None):
        volumes = self.list_volumes()
        return _utils._filter_list(
            volumes, name_or_id, filters)

    def search_volume_snapshots(self, name_or_id=None, filters=None):
        volumesnapshots = self.list_volume_snapshots()
        return _utils._filter_list(
            volumesnapshots, name_or_id, filters)

    def search_volume_backups(self, name_or_id=None, filters=None):
        volume_backups = self.list_volume_backups()
        return _utils._filter_list(
            volume_backups, name_or_id, filters)

    def search_volume_types(
            self, name_or_id=None, filters=None, get_extra=True):
        volume_types = self.list_volume_types(get_extra=get_extra)
        return _utils._filter_list(volume_types, name_or_id, filters)

    def get_volume_type_access(self, name_or_id):
        """Return a list of volume_type_access.

        :param name_or_id: Name or ID of the volume type.

        :raises: OpenStackCloudException on operation error.
        """
        volume_type = self.get_volume_type(name_or_id)
        if not volume_type:
            raise exc.OpenStackCloudException(
                "VolumeType not found: %s" % name_or_id)

        return self.block_storage.get_type_access(volume_type)

    def add_volume_type_access(self, name_or_id, project_id):
        """Grant access on a volume_type to a project.

        :param name_or_id: ID or name of a volume_type
        :param project_id: A project id

        NOTE: the call works even if the project does not exist.

        :raises: OpenStackCloudException on operation error.
        """
        volume_type = self.get_volume_type(name_or_id)
        if not volume_type:
            raise exc.OpenStackCloudException(
                "VolumeType not found: %s" % name_or_id)

        self.block_storage.add_type_access(volume_type, project_id)

    def remove_volume_type_access(self, name_or_id, project_id):
        """Revoke access on a volume_type to a project.

        :param name_or_id: ID or name of a volume_type
        :param project_id: A project id

        :raises: OpenStackCloudException on operation error.
        """
        volume_type = self.get_volume_type(name_or_id)
        if not volume_type:
            raise exc.OpenStackCloudException(
                "VolumeType not found: %s" % name_or_id)
        self.block_storage.remove_type_access(volume_type, project_id)

    def set_volume_quotas(self, name_or_id, **kwargs):
        """ Set a volume quota in a project

        :param name_or_id: project name or id
        :param kwargs: key/value pairs of quota name and quota value

        :raises: OpenStackCloudException if the resource to set the
            quota does not exist.
        """

        proj = self.identity.find_project(
            name_or_id, ignore_missing=False)

        self.block_storage.update_quota_set(
            _qs.QuotaSet(project_id=proj.id),
            **kwargs)

    def get_volume_quotas(self, name_or_id):
        """ Get volume quotas for a project

        :param name_or_id: project name or id
        :raises: OpenStackCloudException if it's not a valid project

        :returns: Munch object with the quotas
        """
        proj = self.identity.find_project(
            name_or_id, ignore_missing=False)

        return self.block_storage.get_quota_set(
            proj)

    def delete_volume_quotas(self, name_or_id):
        """ Delete volume quotas for a project

        :param name_or_id: project name or id
        :raises: OpenStackCloudException if it's not a valid project or the
                 cinder client call failed

        :returns: dict with the quotas
        """
        proj = self.identity.find_project(
            name_or_id, ignore_missing=False)

        return self.block_storage.revert_quota_set(
            proj)
