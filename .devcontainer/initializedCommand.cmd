@rem Copyright 2022 Sony Semiconductor Solutions Corp. All rights reserved.

@rem Licensed under the Apache License, Version 2.0 (the "License");
@rem you may not use this file except in compliance with the License.
@rem You may obtain a copy of the License at

@rem    http://www.apache.org/licenses/LICENSE-2.0

@rem Unless required by applicable law or agreed to in writing, software
@rem distributed under the License is distributed on an "AS IS" BASIS,
@rem WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
@rem See the License for the specific language governing permissions and
@rem limitations under the License.
@echo on

SET CMDDIR=%~dp0

SET LIB=%CMDDIR%Dependencies\aitrios-sdk-console-access-lib-python

dir /b /a  %LIB% | findstr "." >nul && (set EMPTY=0) || (set EMPTY=1)
if %EMPTY% EQU 1 (
    git submodule update --init --recursive .devcontainer\Dependencies\aitrios-sdk-console-access-lib-python
)
