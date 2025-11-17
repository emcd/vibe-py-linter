# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-

#============================================================================#
#                                                                            #
#  Licensed under the Apache License, Version 2.0 (the "License");           #
#  you may not use this file except in compliance with the License.          #
#  You may obtain a copy of the License at                                   #
#                                                                            #
#      http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                            #
#  Unless required by applicable law or agreed to in writing, software       #
#  distributed under the License is distributed on an "AS IS" BASIS,         #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#  See the License for the specific language governing permissions and       #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#


''' Global rule registry initialization. '''


from ..registry import RuleDescriptor as _RuleDescriptor
from ..registry import RuleRegistryManager as _RuleRegistryManager
from .vbl101 import VBL101 as _VBL101


_DESCRIPTORS = {
    'VBL101': _RuleDescriptor(
        vbl_code = 'VBL101',
        descriptive_name = 'blank-line-elimination',
        description = 'Detects blank lines within function bodies.',
        category = 'readability',
        subcategory = 'compactness',
        rule_class = _VBL101,
    ),
}


def create_default_registry_manager( ) -> _RuleRegistryManager:
    ''' Creates the default rule registry manager with all available rules. '''
    return _RuleRegistryManager( _DESCRIPTORS )
