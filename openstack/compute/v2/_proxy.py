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

import warnings

from openstack.compute.v2 import aggregate as _aggregate
from openstack.compute.v2 import availability_zone
from openstack.compute.v2 import extension
from openstack.compute.v2 import flavor as _flavor
from openstack.compute.v2 import hypervisor as _hypervisor
from openstack.compute.v2 import image as _image
from openstack.compute.v2 import keypair as _keypair
from openstack.compute.v2 import limits
from openstack.compute.v2 import migration as _migration
from openstack.compute.v2 import quota_set as _quota_set
from openstack.compute.v2 import server as _server
from openstack.compute.v2 import server_diagnostics as _server_diagnostics
from openstack.compute.v2 import server_group as _server_group
from openstack.compute.v2 import server_interface as _server_interface
from openstack.compute.v2 import server_ip
from openstack.compute.v2 import server_migration as _server_migration
from openstack.compute.v2 import server_remote_console as _src
from openstack.compute.v2 import service as _service
from openstack.compute.v2 import volume_attachment as _volume_attachment
from openstack import exceptions
from openstack.identity.v3 import project as _project
from openstack.network.v2 import security_group as _sg
from openstack import proxy
from openstack import resource
from openstack import utils


class Proxy(proxy.Proxy):

    # ========== Extensions ==========

    def find_extension(self, name_or_id, ignore_missing=True):
        """Find a single extension

        :param name_or_id: The name or ID of an extension.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.compute.v2.extension.Extension` or
            None
        """
        return self._find(extension.Extension, name_or_id,
                          ignore_missing=ignore_missing)

    def extensions(self):
        """Retrieve a generator of extensions

        :returns: A generator of extension instances.
        :rtype: :class:`~openstack.compute.v2.extension.Extension`
        """
        return self._list(extension.Extension)

    # ========== Flavors ==========

    def find_flavor(self, name_or_id, ignore_missing=True,
                    get_extra_specs=False, **query):
        """Find a single flavor

        :param name_or_id: The name or ID of a flavor.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the resource does not exist.  When set to ``True``, None will be
            returned when attempting to find a nonexistent resource.
        :param bool get_extra_specs: When set to ``True`` and extra_specs not
            present in the response will invoke additional API call to fetch
            extra_specs.

        :param kwargs query: Optional query parameters to be sent to limit
            the flavors being returned.

        :returns: One :class:`~openstack.compute.v2.flavor.Flavor` or None
        """
        flavor = self._find(
            _flavor.Flavor, name_or_id, ignore_missing=ignore_missing, **query)
        if flavor and get_extra_specs and not flavor.extra_specs:
            flavor = flavor.fetch_extra_specs(self)
        return flavor

    def create_flavor(self, **attrs):
        """Create a new flavor from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.compute.v2.flavor.Flavor`,
            comprised of the properties on the Flavor class.

        :returns: The results of flavor creation
        :rtype: :class:`~openstack.compute.v2.flavor.Flavor`
        """
        return self._create(_flavor.Flavor, **attrs)

    def delete_flavor(self, flavor, ignore_missing=True):
        """Delete a flavor

        :param flavor: The value can be either the ID of a flavor or a
            :class:`~openstack.compute.v2.flavor.Flavor` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be
            raised when the flavor does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent flavor.

        :returns: ``None``
        """
        self._delete(_flavor.Flavor, flavor, ignore_missing=ignore_missing)

    def update_flavor(self, flavor, **attrs):
        """Update a flavor

        :param server: Either the ID of a flavot or a
            :class:`~openstack.compute.v2.flavor.Flavor` instance.
        :attrs kwargs: The attributes to update on the flavor represented
            by ``flavor``.

        :returns: The updated flavor
        :rtype: :class:`~openstack.compute.v2.flavor.Flavor`
        """
        return self._update(_flavor.Flavor, flavor, **attrs)

    def get_flavor(self, flavor, get_extra_specs=False):
        """Get a single flavor

        :param flavor: The value can be the ID of a flavor or a
            :class:`~openstack.compute.v2.flavor.Flavor` instance.
        :param bool get_extra_specs: When set to ``True`` and extra_specs not
            present in the response will invoke additional API call to fetch
            extra_specs.

        :returns: One :class:`~openstack.compute.v2.flavor.Flavor`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
            when no resource can be found.
        """
        flavor = self._get(_flavor.Flavor, flavor)
        if get_extra_specs and not flavor.extra_specs:
            flavor = flavor.fetch_extra_specs(self)
        return flavor

    def flavors(self, details=True, get_extra_specs=False, **query):
        """Return a generator of flavors

        :param bool details: When ``True``, returns
            :class:`~openstack.compute.v2.flavor.Flavor` objects,
            with additional attributes filled.
        :param bool get_extra_specs: When set to ``True`` and extra_specs not
            present in the response will invoke additional API call to fetch
            extra_specs.
        :param kwargs query: Optional query parameters to be sent to limit
            the flavors being returned.

        :returns: A generator of flavor objects
        """
        base_path = '/flavors/detail' if details else '/flavors'
        for flv in self._list(_flavor.Flavor, base_path=base_path, **query):
            if get_extra_specs and not flv.extra_specs:
                flv = flv.fetch_extra_specs(self)
            yield flv

    def flavor_add_tenant_access(self, flavor, tenant):
        """Adds tenant/project access to flavor.

        :param flavor: Either the ID of a flavor or a
            :class:`~openstack.compute.v2.flavor.Flavor` instance.
        :param str tenant: The UUID of the tenant.

        :returns: One :class:`~openstack.compute.v2.flavor.Flavor`
        """
        flavor = self._get_resource(_flavor.Flavor, flavor)
        return flavor.add_tenant_access(self, tenant)

    def flavor_remove_tenant_access(self, flavor, tenant):
        """Removes tenant/project access to flavor.

        :param flavor: Either the ID of a flavor or a
            :class:`~openstack.compute.v2.flavor.Flavor` instance.
        :param str tenant: The UUID of the tenant.

        :returns: One :class:`~openstack.compute.v2.flavor.Flavor`
        """
        flavor = self._get_resource(_flavor.Flavor, flavor)
        return flavor.remove_tenant_access(self, tenant)

    def get_flavor_access(self, flavor):
        """Lists tenants who have access to private flavor

        :param flavor: Either the ID of a flavor or a
            :class:`~openstack.compute.v2.flavor.Flavor` instance.

        :returns: List of dicts with flavor_id and tenant_id attributes.
        """
        flavor = self._get_resource(_flavor.Flavor, flavor)
        return flavor.get_access(self)

    def fetch_flavor_extra_specs(self, flavor):
        """Lists Extra Specs of a flavor

        :param flavor: Either the ID of a flavor or a
            :class:`~openstack.compute.v2.flavor.Flavor` instance.

        :returns: One :class:`~openstack.compute.v2.flavor.Flavor`
        """
        flavor = self._get_resource(_flavor.Flavor, flavor)
        return flavor.fetch_extra_specs(self)

    def create_flavor_extra_specs(self, flavor, extra_specs):
        """Lists Extra Specs of a flavor

        :param flavor: Either the ID of a flavor or a
            :class:`~openstack.compute.v2.flavor.Flavor` instance.
        :param dict extra_specs: dict of extra specs

        :returns: One :class:`~openstack.compute.v2.flavor.Flavor`
        """
        flavor = self._get_resource(_flavor.Flavor, flavor)
        return flavor.create_extra_specs(self, specs=extra_specs)

    def get_flavor_extra_specs_property(self, flavor, prop):
        """Get specific Extra Spec property of a flavor

        :param flavor: Either the ID of a flavor or a
            :class:`~openstack.compute.v2.flavor.Flavor` instance.
        :param str prop: Property name.

        :returns: String value of the requested property.
        """
        flavor = self._get_resource(_flavor.Flavor, flavor)
        return flavor.get_extra_specs_property(self, prop)

    def update_flavor_extra_specs_property(self, flavor, prop, val):
        """Update specific Extra Spec property of a flavor

        :param flavor: Either the ID of a flavor or a
            :class:`~openstack.compute.v2.flavor.Flavor` instance.
        :param str prop: Property name.
        :param str val: Property value.

        :returns: String value of the requested property.
        """
        flavor = self._get_resource(_flavor.Flavor, flavor)
        return flavor.update_extra_specs_property(self, prop, val)

    def delete_flavor_extra_specs_property(self, flavor, prop):
        """Delete specific Extra Spec property of a flavor

        :param flavor: Either the ID of a flavor or a
            :class:`~openstack.compute.v2.flavor.Flavor` instance.
        :param str prop: Property name.

        :returns: None
        """
        flavor = self._get_resource(_flavor.Flavor, flavor)
        return flavor.delete_extra_specs_property(self, prop)

    # ========== Aggregates ==========

    def aggregates(self, **query):
        """Return a generator of aggregate

        :param kwargs query: Optional query parameters to be sent to limit
            the aggregates being returned.

        :returns: A generator of aggregate
        :rtype: class: `~openstack.compute.v2.aggregate.Aggregate`
        """
        return self._list(_aggregate.Aggregate, **query)

    def get_aggregate(self, aggregate):
        """Get a single host aggregate

        :param image: The value can be the ID of an aggregate or a
            :class:`~openstack.compute.v2.aggregate.Aggregate`
            instance.

        :returns: One :class:`~openstack.compute.v2.aggregate.Aggregate`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
            when no resource can be found.
        """
        return self._get(_aggregate.Aggregate, aggregate)

    def find_aggregate(self, name_or_id, ignore_missing=True):
        """Find a single aggregate

        :param name_or_id: The name or ID of an aggregate.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the resource does not exist.  When set to ``True``, None will be
            returned when attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.compute.v2.aggregate.Aggregate`
            or None
        """
        return self._find(_aggregate.Aggregate, name_or_id,
                          ignore_missing=ignore_missing)

    def create_aggregate(self, **attrs):
        """Create a new host aggregate from attributes

        :param dict attrs: Keyword arguments which will be used to create a
            :class:`~openstack.compute.v2.aggregate.Aggregate`,
            comprised of the properties on the Aggregate class.

        :returns: The results of aggregate creation
        :rtype: :class:`~openstack.compute.v2.aggregate.Aggregate`
        """
        return self._create(_aggregate.Aggregate, **attrs)

    def update_aggregate(self, aggregate, **attrs):
        """Update a host aggregate

        :param server: Either the ID of a host aggregate or a
            :class:`~openstack.compute.v2.aggregate.Aggregate`
            instance.
        :attrs kwargs: The attributes to update on the aggregate represented
            by ``aggregate``.

        :returns: The updated aggregate
        :rtype: :class:`~openstack.compute.v2.aggregate.Aggregate`
        """
        return self._update(_aggregate.Aggregate, aggregate, **attrs)

    def delete_aggregate(self, aggregate, ignore_missing=True):
        """Delete a host aggregate

        :param keypair: The value can be either the ID of an aggregate or a
            :class:`~openstack.compute.v2.aggregate.Aggregate`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be
            raised when the aggregate does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent aggregate.

        :returns: ``None``
        """
        self._delete(_aggregate.Aggregate, aggregate,
                     ignore_missing=ignore_missing)

    def add_host_to_aggregate(self, aggregate, host):
        """Adds a host to an aggregate

        :param aggregate: Either the ID of a aggregate or a
            :class:`~openstack.compute.v2.aggregate.Aggregate`
            instance.
        :param str host: The host to add to the aggregate

        :returns: One :class:`~openstack.compute.v2.aggregate.Aggregate`
        """
        aggregate = self._get_resource(_aggregate.Aggregate, aggregate)
        return aggregate.add_host(self, host)

    def remove_host_from_aggregate(self, aggregate, host):
        """Removes a host from an aggregate

        :param aggregate: Either the ID of a aggregate or a
            :class:`~openstack.compute.v2.aggregate.Aggregate`
            instance.
        :param str host: The host to remove from the aggregate

        :returns: One :class:`~openstack.compute.v2.aggregate.Aggregate`
        """
        aggregate = self._get_resource(_aggregate.Aggregate, aggregate)
        return aggregate.remove_host(self, host)

    def set_aggregate_metadata(self, aggregate, metadata):
        """Creates or replaces metadata for an aggregate

        :param aggregate: Either the ID of a aggregate or a
            :class:`~openstack.compute.v2.aggregate.Aggregate`
            instance.
        :param dict metadata: Metadata key and value pairs. The maximum
            size for each metadata key and value pair
            is 255 bytes.

        :returns: One :class:`~openstack.compute.v2.aggregate.Aggregate`
        """
        aggregate = self._get_resource(_aggregate.Aggregate, aggregate)
        return aggregate.set_metadata(self, metadata)

    def aggregate_precache_images(self, aggregate, images):
        """Requests image precaching on an aggregate

        :param aggregate: Either the ID of a aggregate or a
            :class:`~openstack.compute.v2.aggregate.Aggregate` instance.
        :param images: Single image id or list of image ids.

        :returns: ``None``
        """
        aggregate = self._get_resource(_aggregate.Aggregate, aggregate)
        # We need to ensure we pass list of image IDs
        if isinstance(images, str):
            images = [images]
        image_data = []
        for img in images:
            image_data.append({'id': img})
        return aggregate.precache_images(self, image_data)

    # ========== Images ==========

    def delete_image(self, image, ignore_missing=True):
        """Delete an image

        :param image: The value can be either the ID of an image or a
            :class:`~openstack.compute.v2.image.Image` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be
            raised when the image does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent image.

        :returns: ``None``
        """
        self._delete(_image.Image, image, ignore_missing=ignore_missing)

    def find_image(self, name_or_id, ignore_missing=True):
        """Find a single image

        :param name_or_id: The name or ID of a image.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.compute.v2.image.Image` or None
        """
        return self._find(_image.Image, name_or_id,
                          ignore_missing=ignore_missing)

    def get_image(self, image):
        """Get a single image

        :param image: The value can be the ID of an image or a
            :class:`~openstack.compute.v2.image.Image` instance.

        :returns: One :class:`~openstack.compute.v2.image.Image`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
            when no resource can be found.
        """
        return self._get(_image.Image, image)

    def images(self, details=True, **query):
        """Return a generator of images

        :param bool details: When ``True``, returns
            :class:`~openstack.compute.v2.image.Image` objects with all
            available properties, otherwise only basic properties are returned.
            *Default: ``True``*
        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of image objects
        """
        warnings.warn('This API is deprecated and may disappear shortly',
                      DeprecationWarning)
        base_path = '/images/detail' if details else None
        return self._list(_image.Image, base_path=base_path, **query)

    def _get_base_resource(self, res, base):
        # Metadata calls for Image and Server can work for both those
        # resources but also ImageDetail and ServerDetail. If we get
        # either class, use it, otherwise create an instance of the base.
        if isinstance(res, base):
            return res
        else:
            return base(id=res)

    def get_image_metadata(self, image):
        """Return a dictionary of metadata for an image

        :param image: Either the ID of an image or a
            :class:`~openstack.compute.v2.image.Image` instance.

        :returns: A :class:`~openstack.compute.v2.image.Image` with only the
            image's metadata. All keys and values are Unicode text.
        :rtype: :class:`~openstack.compute.v2.image.Image`
        """
        res = self._get_base_resource(image, _image.Image)
        return res.fetch_metadata(self)

    def set_image_metadata(self, image, **metadata):
        """Update metadata for an image

        :param image: Either the ID of an image or a
            :class:`~openstack.compute.v2.image.Image` instance.
        :param kwargs metadata: Key/value pairs to be updated in the image's
            metadata. No other metadata is modified
            by this call. All keys and values are stored
            as Unicode.

        :returns: A :class:`~openstack.compute.v2.image.Image` with only the
            image's metadata. All keys and values are Unicode text.
        :rtype: :class:`~openstack.compute.v2.image.Image`
        """
        res = self._get_base_resource(image, _image.Image)
        return res.set_metadata(self, metadata=metadata)

    def delete_image_metadata(self, image, keys=None):
        """Delete metadata for an image

        Note: This method will do a HTTP DELETE request for every key in keys.

        :param image: Either the ID of an image or a
            :class:`~openstack.compute.v2.image.Image` instance.
        :param list keys: The keys to delete. If left empty complete metadata
            will be removed.

        :rtype: ``None``
        """
        res = self._get_base_resource(image, _image.Image)
        if keys is not None:
            # Create a set as a snapshot of keys to avoid "changed during
            # iteration"
            for key in set(keys):
                res.delete_metadata_item(self, key)
        else:
            res.delete_metadata(self)

    # ========== Keypairs ==========

    def create_keypair(self, **attrs):
        """Create a new keypair from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.compute.v2.keypair.Keypair`,
            comprised of the properties on the Keypair class.

        :returns: The results of keypair creation
        :rtype: :class:`~openstack.compute.v2.keypair.Keypair`
        """
        return self._create(_keypair.Keypair, **attrs)

    def delete_keypair(self, keypair, ignore_missing=True, user_id=None):
        """Delete a keypair

        :param keypair: The value can be either the ID of a keypair or a
            :class:`~openstack.compute.v2.keypair.Keypair` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the keypair does not exist.  When set to ``True``, no exception
            will be set when attempting to delete a nonexistent keypair.
        :param str user_id: Optional user_id owning the keypair

        :returns: ``None``
        """
        attrs = {'user_id': user_id} if user_id else {}
        self._delete(_keypair.Keypair, keypair, ignore_missing=ignore_missing,
                     **attrs)

    def get_keypair(self, keypair, user_id=None):
        """Get a single keypair

        :param keypair: The value can be the ID of a keypair or a
            :class:`~openstack.compute.v2.keypair.Keypair` instance.
        :param str user_id: Optional user_id owning the keypair

        :returns: One :class:`~openstack.compute.v2.keypair.Keypair`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
            when no resource can be found.
        """
        attrs = {'user_id': user_id} if user_id else {}
        return self._get(_keypair.Keypair, keypair, **attrs)

    def find_keypair(self, name_or_id, ignore_missing=True, user_id=None):
        """Find a single keypair

        :param name_or_id: The name or ID of a keypair.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the resource does not exist.  When set to ``True``, None will be
            returned when attempting to find a nonexistent resource.
        :param str user_id: Optional user_id owning the keypair

        :returns: One :class:`~openstack.compute.v2.keypair.Keypair` or None
        """
        attrs = {'user_id': user_id} if user_id else {}
        return self._find(_keypair.Keypair, name_or_id,
                          ignore_missing=ignore_missing,
                          **attrs)

    def keypairs(self, **query):
        """Return a generator of keypairs

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.
        :returns: A generator of keypair objects
        :rtype: :class:`~openstack.compute.v2.keypair.Keypair`
        """
        return self._list(_keypair.Keypair, **query)

    # ========== Limits ==========

    def get_limits(self, **query):
        """Retrieve limits that are applied to the project's account

        :returns: A Limits object, including both
            :class:`~openstack.compute.v2.limits.AbsoluteLimits` and
            :class:`~openstack.compute.v2.limits.RateLimits`
        :rtype: :class:`~openstack.compute.v2.limits.Limits`
        """
        res = self._get_resource(
            limits.Limits, None)
        return res.fetch(
            self, **query)

    # ========== Servers ==========

    def create_server(self, **attrs):
        """Create a new server from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.compute.v2.server.Server`,
            comprised of the properties on the Server class.

        :returns: The results of server creation
        :rtype: :class:`~openstack.compute.v2.server.Server`
        """
        return self._create(_server.Server, **attrs)

    def delete_server(self, server, ignore_missing=True, force=False):
        """Delete a server

        :param server: The value can be either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be
            raised when the server does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent server
        :param bool force: When set to ``True``, the server deletion will be
            forced immediately.

        :returns: ``None``
        """
        if force:
            server = self._get_resource(_server.Server, server)
            server.force_delete(self)
        else:
            self._delete(_server.Server, server, ignore_missing=ignore_missing)

    def find_server(self, name_or_id, ignore_missing=True):
        """Find a single server

        :param name_or_id: The name or ID of a server.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.compute.v2.server.Server` or None
        """
        return self._find(_server.Server, name_or_id,
                          ignore_missing=ignore_missing)

    def get_server(self, server):
        """Get a single server

        :param server: The value can be the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.

        :returns: One :class:`~openstack.compute.v2.server.Server`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
            when no resource can be found.
        """
        return self._get(_server.Server, server)

    def servers(self, details=True, all_projects=False, **query):
        """Retrieve a generator of servers

        :param bool details: When set to ``False``
            instances with only basic data will be returned. The default,
            ``True``, will cause instances with full data to be returned.
        :param kwargs query: Optional query parameters to be sent to limit
            the servers being returned. Available parameters can be seen
            under https://docs.openstack.org/api-ref/compute/#list-servers

        :returns: A generator of server instances.
        """
        if all_projects:
            query['all_projects'] = True
        base_path = '/servers/detail' if details else None
        return self._list(_server.Server, base_path=base_path, **query)

    def update_server(self, server, **attrs):
        """Update a server

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :attrs kwargs: The attributes to update on the server represented
            by ``server``.

        :returns: The updated server
        :rtype: :class:`~openstack.compute.v2.server.Server`
        """
        return self._update(_server.Server, server, **attrs)

    def change_server_password(self, server, new_password):
        """Change the administrator password

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :param str new_password: The new password to be set.

        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.change_password(self, new_password)

    def get_server_password(self, server):
        """Get the administrator password

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.

        :returns: encrypted password.
        """
        server = self._get_resource(_server.Server, server)
        return server.get_password(self)

    def reset_server_state(self, server, state):
        """Reset the state of server

        :param server: The server can be either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server`.
        :param state: The state of the server to be set, `active` or
            `error` are valid.

        :returns: None
        """
        res = self._get_base_resource(server, _server.Server)
        res.reset_state(self, state)

    def reboot_server(self, server, reboot_type):
        """Reboot a server

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :param str reboot_type: The type of reboot to perform.
            "HARD" and "SOFT" are the current options.

        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.reboot(self, reboot_type)

    def rebuild_server(self, server, image, **attrs):
        """Rebuild a server

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :param str name: The name of the server
        :param str admin_password: The administrator password
        :param bool preserve_ephemeral: Indicates whether the server
            is rebuilt with the preservation of the ephemeral partition.
            *Default: False*
        :param str image: The id of an image to rebuild with. *Default: None*
        :param str access_ipv4: The IPv4 address to rebuild with.
            *Default: None*
        :param str access_ipv6: The IPv6 address to rebuild with.
            *Default: None*
        :param dict metadata: A dictionary of metadata to rebuild with.
            *Default: None*
        :param personality: A list of dictionaries, each including a
            **path** and **contents** key, to be injected
            into the rebuilt server at launch.
            *Default: None*

        :returns: The rebuilt :class:`~openstack.compute.v2.server.Server`
            instance.
        """
        server = self._get_resource(_server.Server, server)
        return server.rebuild(self, image=image, **attrs)

    def resize_server(self, server, flavor):
        """Resize a server

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :param flavor: Either the ID of a flavor or a
            :class:`~openstack.compute.v2.flavor.Flavor` instance.

        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        flavor_id = resource.Resource._get_id(flavor)
        server.resize(self, flavor_id)

    def confirm_server_resize(self, server):
        """Confirm a server resize

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.

        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.confirm_resize(self)

    def revert_server_resize(self, server):
        """Revert a server resize

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.

        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.revert_resize(self)

    def create_server_image(self, server, name, metadata=None, wait=False,
                            timeout=120):
        """Create an image from a server

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :param str name: The name of the image to be created.
        :param dict metadata: A dictionary of metadata to be set on the image.

        :returns: :class:`~openstack.image.v2.image.Image` object.
        """
        server = self._get_resource(_server.Server, server)
        image_id = server.create_image(self, name, metadata)

        self._connection.list_images.invalidate(self)
        image = self._connection.get_image(image_id)

        if not wait:
            return image
        return self._connection.wait_for_image(image, timeout=timeout)

    def backup_server(self, server, name, backup_type, rotation):
        """Backup a server

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :param name: The name of the backup image.
        :param backup_type: The type of the backup, for example, daily.
        :param rotation: The rotation of the back up image, the oldest
            image will be removed when image count exceed
            the rotation count.

        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.backup(self, name, backup_type, rotation)

    def pause_server(self, server):
        """Pauses a server and changes its status to ``PAUSED``.

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.pause(self)

    def unpause_server(self, server):
        """Unpauses a paused server and changes its status to ``ACTIVE``.

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.unpause(self)

    def suspend_server(self, server):
        """Suspends a server and changes its status to ``SUSPENDED``.

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.suspend(self)

    def resume_server(self, server):
        """Resumes a suspended server and changes its status to ``ACTIVE``.

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.resume(self)

    def lock_server(self, server, locked_reason=None):
        """Locks a server.

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :param locked_reason: The reason behind locking the server. Limited to
            255 characters in length.
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.lock(self, locked_reason=locked_reason)

    def unlock_server(self, server):
        """Unlocks a locked server.

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.unlock(self)

    def rescue_server(self, server, admin_pass=None, image_ref=None):
        """Puts a server in rescue mode and changes it status to ``RESCUE``.

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :param admin_pass: The password for the rescued server. If you omit
            this parameter, the operation generates a new
            password.
        :param image_ref: The image reference to use to rescue your server.
            This can be the image ID or its full URL. If you
            omit this parameter, the base image reference will
            be used.
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.rescue(self, admin_pass=admin_pass,
                      image_ref=image_ref)

    def unrescue_server(self, server):
        """Unrescues a server and changes its status to ``ACTIVE``.

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.unrescue(self)

    def evacuate_server(self, server, host=None, admin_pass=None, force=None):
        """Evacuates a server from a failed host to a new host.

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :param host: An optional parameter specifying the name or ID of the
            host to which the server is evacuated.
        :param admin_pass: An optional parameter specifying the administrative
            password to access the evacuated or rebuilt server.
        :param force: Force an evacuation by not verifying the provided
            destination host by the scheduler. (New in API version
            2.29).
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.evacuate(self, host=host, admin_pass=admin_pass,
                        force=force)

    def start_server(self, server):
        """Starts a stopped server and changes its state to ``ACTIVE``.

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.start(self)

    def stop_server(self, server):
        """Stops a running server and changes its state to ``SHUTOFF``.

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.stop(self)

    def shelve_server(self, server):
        """Shelves a server.

        All associated data and resources are kept but anything still in
        memory is not retained. Policy defaults enable only users with
        administrative role or the owner of the server to perform this
        operation. Cloud provides could change this permission though.

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.shelve(self)

    def unshelve_server(self, server):
        """Unselves or restores a shelved server.

        Policy defaults enable only users with administrative role or the
        owner of the server to perform this operation. Cloud provides could
        change this permission though.

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.unshelve(self)

    # ========== Server security groups ==========

    def fetch_server_security_groups(self, server):
        """Fetch security groups with details for a server.

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.

        :returns: updated :class:`~openstack.compute.v2.server.Server` instance
        """
        server = self._get_resource(_server.Server, server)
        return server.fetch_security_groups(self)

    def add_security_group_to_server(self, server, security_group):
        """Add a security group to a server

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :param security_group: Either the ID, Name of a security group or a
            :class:`~openstack.network.v2.security_group.SecurityGroup`
            instance.

        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        security_group = self._get_resource(_sg.SecurityGroup, security_group)
        server.add_security_group(self, security_group.name)

    def remove_security_group_from_server(self, server, security_group):
        """Remove a security group from a server

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :param security_group: Either the ID of a security group or a
            :class:`~openstack.network.v2.security_group.SecurityGroup`
            instance.

        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        security_group = self._get_resource(_sg.SecurityGroup, security_group)
        server.remove_security_group(self, security_group.name)

    # ========== Server IPs ==========

    def add_fixed_ip_to_server(self, server, network_id):
        """Adds a fixed IP address to a server instance.

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :param network_id: The ID of the network from which a fixed IP address
            is about to be allocated.
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.add_fixed_ip(self, network_id)

    def remove_fixed_ip_from_server(self, server, address):
        """Removes a fixed IP address from a server instance.

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :param address: The fixed IP address to be disassociated from the
            server.
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.remove_fixed_ip(self, address)

    def add_floating_ip_to_server(self, server, address, fixed_address=None):
        """Adds a floating IP address to a server instance.

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :param address: The floating IP address to be added to the server.
        :param fixed_address: The fixed IP address to be associated with the
            floating IP address. Used when the server is
            connected to multiple networks.
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.add_floating_ip(self, address,
                               fixed_address=fixed_address)

    def remove_floating_ip_from_server(self, server, address):
        """Removes a floating IP address from a server instance.

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :param address: The floating IP address to be disassociated from the
            server.
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.remove_floating_ip(self, address)

    # ========== Server Interfaces ==========

    def create_server_interface(self, server, **attrs):
        """Create a new server interface from attributes

        :param server: The server can be either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance
                       that the interface belongs to.
        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.compute.v2.server_interface.ServerInterface`,
            comprised of the properties on the ServerInterface class.

        :returns: The results of server interface creation
        :rtype: :class:`~openstack.compute.v2.server_interface.ServerInterface`
        """
        server_id = resource.Resource._get_id(server)
        return self._create(_server_interface.ServerInterface,
                            server_id=server_id, **attrs)

    # TODO(stephenfin): Does this work? There's no 'value' parameter for the
    # call to '_delete'
    def delete_server_interface(self, server_interface, server=None,
                                ignore_missing=True):
        """Delete a server interface

        :param server_interface:
            The value can be either the ID of a server interface or a
            :class:`~openstack.compute.v2.server_interface.ServerInterface`
            instance.
        :param server: This parameter need to be specified when ServerInterface
            ID is given as value. It can be either the ID of a
            server or a :class:`~openstack.compute.v2.server.Server`
            instance that the interface belongs to.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be
            raised when the server interface does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent server interface.

        :returns: ``None``
        """
        server_id = self._get_uri_attribute(server_interface, server,
                                            "server_id")
        server_interface = resource.Resource._get_id(server_interface)

        self._delete(_server_interface.ServerInterface,
                     server_interface,
                     server_id=server_id,
                     ignore_missing=ignore_missing)

    def get_server_interface(self, server_interface, server=None):
        """Get a single server interface

        :param server_interface:
            The value can be the ID of a server interface or a
            :class:`~openstack.compute.v2.server_interface.ServerInterface`
            instance.
        :param server: This parameter need to be specified when ServerInterface
            ID is given as value. It can be either the ID of a
            server or a :class:`~openstack.compute.v2.server.Server`
            instance that the interface belongs to.

        :returns: One
            :class:`~openstack.compute.v2.server_interface.ServerInterface`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
            when no resource can be found.
        """
        server_id = self._get_uri_attribute(server_interface, server,
                                            "server_id")
        server_interface = resource.Resource._get_id(server_interface)

        return self._get(_server_interface.ServerInterface,
                         server_id=server_id, port_id=server_interface)

    def server_interfaces(self, server, **query):
        """Return a generator of server interfaces

        :param server: The server can be either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server`.
        :param query: Optional query parameters to be sent to limit the
            resources being returned.

        :returns: A generator of ServerInterface objects
        :rtype: :class:`~openstack.compute.v2.server_interface.ServerInterface`
        """
        server_id = resource.Resource._get_id(server)
        return self._list(_server_interface.ServerInterface,
                          server_id=server_id, **query)

    def server_ips(self, server, network_label=None):
        """Return a generator of server IPs

        :param server: The server can be either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server`.
        :param network_label: The name of a particular network to list
            IP addresses from.

        :returns: A generator of ServerIP objects
        :rtype: :class:`~openstack.compute.v2.server_ip.ServerIP`
        """
        server_id = resource.Resource._get_id(server)
        return self._list(server_ip.ServerIP,
                          server_id=server_id, network_label=network_label)

    def availability_zones(self, details=False):
        """Return a generator of availability zones

        :param bool details: Return extra details about the availability
            zones. This defaults to `False` as it generally
            requires extra permission.

        :returns: A generator of availability zone
        :rtype:
            :class:`~openstack.compute.v2.availability_zone.AvailabilityZone`
        """
        base_path = '/os-availability-zone/detail' if details else None

        return self._list(
            availability_zone.AvailabilityZone,
            base_path=base_path)

    # ========== Server Metadata ==========

    def get_server_metadata(self, server):
        """Return a dictionary of metadata for a server

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` or
            :class:`~openstack.compute.v2.server.ServerDetail`
            instance.

        :returns: A :class:`~openstack.compute.v2.server.Server` with the
            server's metadata. All keys and values are Unicode text.
        :rtype: :class:`~openstack.compute.v2.server.Server`
        """
        res = self._get_base_resource(server, _server.Server)
        return res.fetch_metadata(self)

    def set_server_metadata(self, server, **metadata):
        """Update metadata for a server

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :param kwargs metadata: Key/value pairs to be updated in the server's
            metadata. No other metadata is modified
            by this call. All keys and values are stored
            as Unicode.

        :returns: A :class:`~openstack.compute.v2.server.Server` with only the
            server's metadata. All keys and values are Unicode text.
        :rtype: :class:`~openstack.compute.v2.server.Server`
        """
        res = self._get_base_resource(server, _server.Server)
        return res.set_metadata(self, metadata=metadata)

    def delete_server_metadata(self, server, keys=None):
        """Delete metadata for a server

        Note: This method will do a HTTP DELETE request for every key in keys.

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :param list keys: The keys to delete. If left empty complete
            metadata will be removed.

        :rtype: ``None``
        """
        res = self._get_base_resource(server, _server.Server)
        if keys is not None:
            # Create a set as a snapshot of keys to avoid "changed during
            # iteration"
            for key in set(keys):
                res.delete_metadata_item(self, key)
        else:
            res.delete_metadata(self)

    # ========== Server Groups ==========

    def create_server_group(self, **attrs):
        """Create a new server group from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.compute.v2.server_group.ServerGroup`,
            comprised of the properties on the ServerGroup class.

        :returns: The results of server group creation
        :rtype: :class:`~openstack.compute.v2.server_group.ServerGroup`
        """
        return self._create(_server_group.ServerGroup, **attrs)

    def delete_server_group(self, server_group, ignore_missing=True):
        """Delete a server group

        :param server_group: The value can be either the ID of a server group
            or a :class:`~openstack.compute.v2.server_group.ServerGroup`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be
            raised when the server group does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent server group.

        :returns: ``None``
        """
        self._delete(_server_group.ServerGroup, server_group,
                     ignore_missing=ignore_missing)

    def find_server_group(self, name_or_id, ignore_missing=True):
        """Find a single server group

        :param name_or_id: The name or ID of a server group.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns:
            One :class:`~openstack.compute.v2.server_group.ServerGroup` object
            or None
        """
        return self._find(_server_group.ServerGroup, name_or_id,
                          ignore_missing=ignore_missing)

    def get_server_group(self, server_group):
        """Get a single server group

        :param server_group: The value can be the ID of a server group or a
            :class:`~openstack.compute.v2.server_group.ServerGroup`
            instance.

        :returns:
            A :class:`~openstack.compute.v2.server_group.ServerGroup` object.
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
            when no resource can be found.
        """
        return self._get(_server_group.ServerGroup, server_group)

    def server_groups(self, **query):
        """Return a generator of server groups

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of ServerGroup objects
        :rtype: :class:`~openstack.compute.v2.server_group.ServerGroup`
        """
        return self._list(_server_group.ServerGroup, **query)

    # ========== Hypervisors ==========

    def hypervisors(self, details=False, **query):
        """Return a generator of hypervisor

        :param bool details: When set to the default, ``False``,
            :class:`~openstack.compute.v2.hypervisor.Hypervisor`
            instances will be returned with only basic information populated.
        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.
        :returns: A generator of hypervisor
        :rtype: class: `~openstack.compute.v2.hypervisor.Hypervisor`
        """
        base_path = '/os-hypervisors/detail' if details else None
        if (
            'hypervisor_hostname_pattern' in query
            and not utils.supports_microversion(self, '2.53')
        ):
            # Until 2.53 we need to use other API
            base_path = '/os-hypervisors/{pattern}/search'.format(
                pattern=query.pop('hypervisor_hostname_pattern'))
        return self._list(_hypervisor.Hypervisor, base_path=base_path, **query)

    def find_hypervisor(self, name_or_id, ignore_missing=True, details=True):
        """Find a hypervisor from name or id to get the corresponding info

        :param name_or_id: The name or id of a hypervisor

        :returns:
            One: class:`~openstack.compute.v2.hypervisor.Hypervisor` object
            or None
        """

        list_base_path = '/os-hypervisors/detail' if details else None
        return self._find(_hypervisor.Hypervisor, name_or_id,
                          list_base_path=list_base_path,
                          ignore_missing=ignore_missing)

    def get_hypervisor(self, hypervisor):
        """Get a single hypervisor

        :param hypervisor: The value can be the ID of a hypervisor or a
            :class:`~openstack.compute.v2.hypervisor.Hypervisor`
            instance.

        :returns:
            A :class:`~openstack.compute.v2.hypervisor.Hypervisor` object.
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
            when no resource can be found.
        """
        return self._get(_hypervisor.Hypervisor, hypervisor)

    def get_hypervisor_uptime(self, hypervisor):
        """Get uptime information for hypervisor

        :param hypervisor: The value can be the ID of a hypervisor or a
            :class:`~openstack.compute.v2.hypervisor.Hypervisor`
            instance.

        :returns:
            A :class:`~openstack.compute.v2.hypervisor.Hypervisor` object.
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
            when no resource can be found.
        """
        hypervisor = self._get_resource(_hypervisor.Hypervisor, hypervisor)
        return hypervisor.get_uptime(self)

    # ========== Services ==========

    def update_service_forced_down(
        self, service, host=None, binary=None, forced=True
    ):
        """Update service forced_down information

        :param service: Either the ID of a service or a
            :class:`~openstack.compute.v2.service.Service` instance.
        :param str host: The host where service runs.
        :param str binary: The name of service.
        :param bool forced: Whether or not this service was forced down
            manually by an administrator after the service was fenced.

        :returns: Updated service instance
        :rtype: class: `~openstack.compute.v2.service.Service`
        """
        if utils.supports_microversion(self, '2.53'):
            return self.update_service(
                service, forced_down=forced)

        service = self._get_resource(_service.Service, service)
        if (
            (not host or not binary)
            and (not service.host or not service.binary)
        ):
            raise ValueError(
                'Either service instance should have host and binary '
                'or they should be passed')
        service.set_forced_down(self, host, binary, forced)

    force_service_down = update_service_forced_down

    def disable_service(
        self, service, host=None, binary=None, disabled_reason=None
    ):
        """Disable a service

        :param service: Either the ID of a service or a
            :class:`~openstack.compute.v2.service.Service` instance.
        :param str host: The host where service runs.
        :param str binary: The name of service.
        :param str disabled_reason: The reason of force down a service.

        :returns: Updated service instance
        :rtype: class: `~openstack.compute.v2.service.Service`
        """
        if utils.supports_microversion(self, '2.53'):
            attrs = {
                'status': 'disabled'
            }
            if disabled_reason:
                attrs['disabled_reason'] = disabled_reason
            return self.update_service(
                service, **attrs)

        service = self._get_resource(_service.Service, service)
        return service.disable(
            self, host, binary, disabled_reason)

    def enable_service(self, service, host=None, binary=None):
        """Enable a service

        :param service: Either the ID of a service or a
            :class:`~openstack.compute.v2.service.Service` instance.
        :param str host: The host where service runs.
        :param str binary: The name of service.

        :returns: Updated service instance
        :rtype: class: `~openstack.compute.v2.service.Service`
        """
        if utils.supports_microversion(self, '2.53'):
            return self.update_service(
                service, status='enabled')

        service = self._get_resource(_service.Service, service)
        return service.enable(self, host, binary)

    def services(self, **query):
        """Return a generator of service

        :params dict query: Query parameters
        :returns: A generator of service
        :rtype: class: `~openstack.compute.v2.service.Service`
        """
        return self._list(_service.Service, **query)

    def find_service(self, name_or_id, ignore_missing=True, **attrs):
        """Find a service from name or id to get the corresponding info

        :param name_or_id: The name or id of a service
        :param dict attrs: Additional attributes like 'host'

        :returns:
            One: class:`~openstack.compute.v2.hypervisor.Hypervisor` object
            or None
        """
        return self._find(_service.Service, name_or_id,
                          ignore_missing=ignore_missing, **attrs)

    def delete_service(self, service, ignore_missing=True):
        """Delete a service

        :param service:
            The value can be either the ID of a service or a
            :class:`~openstack.compute.v2.service.Service` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the volume attachment does not exist.  When set to ``True``, no
            exception will be set when attempting to delete a nonexistent
            volume attachment.

        :returns: ``None``
        """
        self._delete(
            _service.Service, service, ignore_missing=ignore_missing)

    def update_service(self, service, **attrs):
        """Update a service

        :param server: Either the ID of a service or a
            :class:`~openstack.compute.v2.service.Service` instance.
        :attrs kwargs: The attributes to update on the service represented
            by ``service``.

        :returns: The updated service
        :rtype: :class:`~openstack.compute.v2.service.Service`
        """
        if utils.supports_microversion(self, '2.53'):
            return self._update(_service.Service, service, **attrs)

        raise exceptions.SDKException(
            'Method require at least microversion 2.53'
        )

    # ========== Volume Attachments ==========

    def create_volume_attachment(self, server, **attrs):
        """Create a new volume attachment from attributes

        :param server: The server can be either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :param dict attrs: Keyword arguments which will be used to create a
            :class:`~openstack.compute.v2.volume_attachment.VolumeAttachment`,
            comprised of the properties on the VolumeAttachment class.

        :returns: The results of volume attachment creation
        :rtype:
            :class:`~openstack.compute.v2.volume_attachment.VolumeAttachment`
        """
        server_id = resource.Resource._get_id(server)
        return self._create(_volume_attachment.VolumeAttachment,
                            server_id=server_id, **attrs)

    def update_volume_attachment(self, volume_attachment, server,
                                 **attrs):
        """update a volume attachment

        :param volume_attachment:
            The value can be either the ID of a volume attachment or a
            :class:`~openstack.compute.v2.volume_attachment.VolumeAttachment`
            instance.
        :param server: This parameter need to be specified when
            VolumeAttachment ID is given as value. It can be
            either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server`
            instance that the attachment belongs to.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be
            raised when the volume attachment does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent volume  attachment.

        :returns: ``None``
        """
        server_id = self._get_uri_attribute(volume_attachment, server,
                                            "server_id")
        volume_attachment = resource.Resource._get_id(volume_attachment)

        return self._update(_volume_attachment.VolumeAttachment,
                            attachment_id=volume_attachment,
                            server_id=server_id)

    def delete_volume_attachment(self, volume_attachment, server,
                                 ignore_missing=True):
        """Delete a volume attachment

        :param volume_attachment:
            The value can be either the ID of a volume attachment or a
            :class:`~openstack.compute.v2.volume_attachment.VolumeAttachment`
            instance.
        :param server: This parameter need to be specified when
            VolumeAttachment ID is given as value. It can be either
            the ID of a server or a
            :class:`~openstack.compute.v2.server.Server`
            instance that the attachment belongs to.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be
            raised when the volume attachment does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent volume attachment.

        :returns: ``None``
        """
        server_id = self._get_uri_attribute(volume_attachment, server,
                                            "server_id")
        volume_attachment = resource.Resource._get_id(volume_attachment)

        self._delete(_volume_attachment.VolumeAttachment,
                     attachment_id=volume_attachment,
                     server_id=server_id,
                     ignore_missing=ignore_missing)

    def get_volume_attachment(self, volume_attachment, server,
                              ignore_missing=True):
        """Get a single volume attachment

        :param volume_attachment:
            The value can be the ID of a volume attachment or a
            :class:`~openstack.compute.v2.volume_attachment.VolumeAttachment`
            instance.
        :param server: This parameter need to be specified when
            VolumeAttachment ID is given as value. It can be either
            the ID of a server or a
            :class:`~openstack.compute.v2.server.Server`
            instance that the attachment belongs to.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be
            raised when the volume attachment does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent volume attachment.

        :returns: One
            :class:`~openstack.compute.v2.volume_attachment.VolumeAttachment`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
            when no resource can be found.
        """
        server_id = self._get_uri_attribute(volume_attachment, server,
                                            "server_id")
        volume_attachment = resource.Resource._get_id(volume_attachment)

        return self._get(_volume_attachment.VolumeAttachment,
                         server_id=server_id,
                         attachment_id=volume_attachment,
                         ignore_missing=ignore_missing)

    def volume_attachments(self, server):
        """Return a generator of volume attachments

        :param server: The server can be either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server`.

        :returns: A generator of VolumeAttachment objects
        :rtype:
            :class:`~openstack.compute.v2.volume_attachment.VolumeAttachment`
        """
        server_id = resource.Resource._get_id(server)
        return self._list(_volume_attachment.VolumeAttachment,
                          server_id=server_id)

    # ========== Server Migrations ==========

    def migrate_server(self, server):
        """Migrate a server from one host to another

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.migrate(self)

    def live_migrate_server(
        self, server, host=None, force=False, block_migration=None,
    ):
        """Live migrate a server from one host to target host

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :param str host: The host to which to migrate the server. If the Nova
            service is too old, the host parameter implies force=True which
            causes the Nova scheduler to be bypassed. On such clouds, a
            ``ValueError`` will be thrown if ``host`` is given without
            ``force``.
        :param bool force: Force a live-migration by not verifying the provided
            destination host by the scheduler. This is unsafe and not
            recommended.
        :param block_migration: Perform a block live migration to the
            destination host by the scheduler.  Can be 'auto', True or False.
            Some clouds are too old to support 'auto', in which case a
            ValueError will be thrown. If omitted, the value will be 'auto' on
            clouds that support it, and False on clouds that do not.
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.live_migrate(
            self, host,
            force=force,
            block_migration=block_migration,
        )

    def abort_server_migration(
        self, server_migration, server, ignore_missing=True,
    ):
        """Abort an in-progress server migration

        :param server_migration: The value can be either the ID of a server
            migration or a
            :class:`~openstack.compute.v2.server_migration.ServerMigration`
            instance.
        :param server: This parameter needs to be specified when
            ServerMigration ID is given as value. It can be either the ID of a
            server or a :class:`~openstack.compute.v2.server.Server` instance
            that the migration belongs to.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the volume attachment does not exist. When set to ``True``, no
            exception will be set when attempting to delete a nonexistent
            volume attachment.

        :returns: ``None``
        """
        server_id = self._get_uri_attribute(
            server_migration, server, 'server_id',
        )
        server_migration = resource.Resource._get_id(server_migration)

        self._delete(
            _server_migration.ServerMigration,
            server_migration,
            server_id=server_id,
            ignore_missing=ignore_missing,
        )

    def force_complete_server_migration(self, server_migration, server=None):
        """Force complete an in-progress server migration

        :param server_migration: The value can be either the ID of a server
            migration or a
            :class:`~openstack.compute.v2.server_migration.ServerMigration`
            instance.
        :param server: This parameter needs to be specified when
            ServerMigration ID is given as value. It can be either the ID of a
            server or a :class:`~openstack.compute.v2.server.Server` instance
            that the migration belongs to.

        :returns: ``None``
        """
        server_id = self._get_uri_attribute(
            server_migration, server, 'server_id',
        )
        server_migration = self._get_resource(
            _server_migration.ServerMigration,
            server_migration,
            server_id=server_id,
        )
        server_migration.force_complete(self)

    def get_server_migration(
        self,
        server_migration,
        server,
        ignore_missing=True,
    ):
        """Get a single volume attachment

        :param server_migration: The value can be the ID of a server migration
            or a
            :class:`~openstack.compute.v2.server_migration.ServerMigration`
            instance.
        :param server: This parameter need to be specified when ServerMigration
            ID is given as value. It can be either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance that the
            migration belongs to.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the server migration does not exist. When set to ``True``, no
            exception will be set when attempting to delete a nonexistent
            server migration.

        :returns: One
            :class:`~openstack.compute.v2.server_migration.ServerMigration`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
            when no resource can be found.
        """
        server_id = self._get_uri_attribute(
            server_migration, server, 'server_id',
        )
        server_migration = resource.Resource._get_id(server_migration)

        return self._get(
            _server_migration.ServerMigration,
            server_migration,
            server_id=server_id,
            ignore_missing=ignore_missing,
        )

    def server_migrations(self, server):
        """Return a generator of migrations for a server.

        :param server: The server can be either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server`.

        :returns: A generator of ServerMigration objects
        :rtype:
            :class:`~openstack.compute.v2.server_migration.ServerMigration`
        """
        server_id = resource.Resource._get_id(server)
        return self._list(
            _server_migration.ServerMigration,
            server_id=server_id,
        )

    # ========== Migrations ==========

    def migrations(self):
        """Return a generator of migrations for all servers.

        :returns: A generator of Migration objects
        :rtype: :class:`~openstack.compute.v2.migration.Migration`
        """
        return self._list(_migration.Migration)

    # ========== Server diagnostics ==========

    def get_server_diagnostics(self, server):
        """Get a single server diagnostics

        :param server: This parameter need to be specified when ServerInterface
            ID is given as value. It can be either the ID of a
            server or a :class:`~openstack.compute.v2.server.Server`
            instance that the interface belongs to.

        :returns: One
            :class:`~openstack.compute.v2.server_diagnostics.ServerDiagnostics`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
            when no resource can be found.
        """
        server_id = self._get_resource(_server.Server, server).id
        return self._get(_server_diagnostics.ServerDiagnostics,
                         server_id=server_id, requires_id=False)

    # ========== Server consoles ==========

    def create_server_remote_console(self, server, **attrs):
        """Create a remote console on the server.

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :returns: One
            :class:`~openstack.compute.v2.server_remote_console.ServerRemoteConsole`
        """
        server_id = resource.Resource._get_id(server)
        return self._create(_src.ServerRemoteConsole,
                            server_id=server_id, **attrs)

    def get_server_console_url(self, server, console_type):
        """Create a remote console on the server.

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :param console_type: Type of the console connection.
        :returns: Dictionary with console type and url
        """
        server = self._get_resource(_server.Server, server)
        return server.get_console_url(self, console_type)

    def get_server_console_output(self, server, length=None):
        """Return the console output for a server.

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :param length: Optional number of line to fetch from the end of console
            log. All lines will be returned if this is not specified.
        :returns: The console output as a dict. Control characters will be
            escaped to create a valid JSON string.
        """
        server = self._get_resource(_server.Server, server)
        return server.get_console_output(self, length=length)

    def create_console(self, server, console_type, console_protocol=None):
        """Create a remote console on the server.

        When microversion supported is higher then 2.6 remote console is
        created, otherwise deprecated call to get server console is issued.

        :param server: Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :param console_type: Type of the remote console. Supported values as:
            * novnc
            * spice-html5
            * rdp-html5
            * serial
            * webmks (supported after 2.8)
        :param console_protocol: Optional console protocol (is respected only
            after microversion 2.6).

        :returns: Dictionary with console type, url and optionally protocol.
        """
        server = self._get_resource(_server.Server, server)
        # NOTE: novaclient supports undocumented type xcpvnc also supported
        # historically by OSC. We support it, but do not document either.
        if utils.supports_microversion(self, '2.6'):
            console = self._create(
                _src.ServerRemoteConsole,
                server_id=server.id,
                type=console_type,
                protocol=console_protocol)
            return console.to_dict()
        else:
            return server.get_console_url(self, console_type)

    # ========== Quota sets ==========

    def get_quota_set(self, project, usage=False, **query):
        """Show QuotaSet information for the project

        :param project: ID or instance of
            :class:`~openstack.identity.project.Project` of the project for
            which the quota should be retrieved
        :param bool usage: When set to ``True`` quota usage and reservations
            would be filled.
        :param dict query: Additional query parameters to use.

        :returns: One :class:`~openstack.compute.v2.quota_set.QuotaSet`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
            when no resource can be found.
        """
        project = self._get_resource(_project.Project, project)
        res = self._get_resource(
            _quota_set.QuotaSet, None, project_id=project.id)
        if not query:
            query = {}
        return res.fetch(
            self, usage=usage, **query)

    def get_quota_set_defaults(self, project):
        """Show QuotaSet defaults for the project

        :param project: ID or instance of
            :class:`~openstack.identity.project.Project` of the project for
            which the quota should be retrieved

        :returns: One :class:`~openstack.compute.v2.quota_set.QuotaSet`
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
            :class:`~openstack.compute.v2.quota_set.QuotaSet` instance.
        :param dict query: Optional parameters to be used with update call.
        :attrs kwargs: The attributes to update on the QuotaSet represented
            by ``quota_set``.

        :returns: The updated QuotaSet
        :rtype: :class:`~openstack.compute.v2.quota_set.QuotaSet`
        """
        res = self._get_resource(_quota_set.QuotaSet, quota_set, **attrs)
        if not query:
            query = {}
        return res.commit(self, **query)

    # ========== Utilities ==========

    def wait_for_server(
        self, server, status='ACTIVE', failures=None, interval=2, wait=120,
    ):
        """Wait for a server to be in a particular status.

        :param server: The :class:`~openstack.compute.v2.server.Server` to wait
            on to reach the specified status.
        :type server: :class:`~openstack.compute.v2.server.Server`:
        :param status: Desired status.
        :type status: str
        :param failures: Statuses that would be interpreted as failures.
        :type failures: :py:class:`list`
        :param interval: Number of seconds to wait before to consecutive
            checks. Default to 2.
        :type interval: int
        :param wait: Maximum number of seconds to wait before the change.
            Default to 120.
        :type wait: int
        :returns: The resource is returned on success.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if transition
            to the desired status failed to occur in specified seconds.
        :raises: :class:`~openstack.exceptions.ResourceFailure` if the resource
            has transited to one of the failure statuses.
        :raises: :class:`~AttributeError` if the resource does not have a
            ``status`` attribute.
        """
        failures = ['ERROR'] if failures is None else failures
        return resource.wait_for_status(
            self, server, status, failures, interval, wait,
        )

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

    def _get_cleanup_dependencies(self):
        return {
            'compute': {
                'before': ['block_storage', 'network', 'identity']
            }
        }

    def _service_cleanup(self, dry_run=True, client_status_queue=None,
                         identified_resources=None,
                         filters=None, resource_evaluation_fn=None):
        servers = []
        for obj in self.servers():
            need_delete = self._service_cleanup_del_res(
                self.delete_server,
                obj,
                dry_run=dry_run,
                client_status_queue=client_status_queue,
                identified_resources=identified_resources,
                filters=filters,
                resource_evaluation_fn=resource_evaluation_fn)
            if not dry_run and need_delete:
                # In the dry run we identified, that server will go. To propely
                # identify consequences we need to tell others, that the port
                # will disappear as well
                for port in self._connection.network.ports(device_id=obj.id):
                    identified_resources[port.id] = port
                servers.append(obj)

        # We actually need to wait for servers to really disappear, since they
        # might be still holding ports on the subnet
        for server in servers:
            self.wait_for_delete(server)
