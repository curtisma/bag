# SPDX-License-Identifier: BSD-3-Clause AND Apache-2.0
# Copyright 2018 Regents of the University of California
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Copyright 2019 Blue Cheetah Analog Design Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Generate setup yaml files for various netlist outputs

Please run this script through the generate_netlist_config.sh shell script, which will setup
the PYTHONPATH correctly.
"""

from typing import Dict, Any, Tuple, List

import copy
import argparse
from pathlib import Path

from jinja2 import Environment, DictLoader

from pybag.enum import DesignOutput

from bag.io.file import read_yaml, write_yaml, open_file

netlist_map_default = {
    'basic': {
        'cds_thru': {
            'lib_name': 'basic',
            'cell_name': 'cds_thru',
            'in_terms': [],
            'io_terms': ['src', 'dst'],
            'is_prim': True,
            'nets': [],
            'out_terms': [],
            'props': {},
            'ignore': False,
        },
        'noConn': {
            'lib_name': 'basic',
            'cell_name': 'noConn',
            'in_terms': [],
            'io_terms': ['noConn'],
            'is_prim': True,
            'nets': [],
            'out_terms': [],
            'props': {},
            'ignore': True,
        },
    },
    'analogLib': {
        'cap': {
            'lib_name': 'analogLib',
            'cell_name': 'cap',
            'in_terms': [],
            'io_terms': ['PLUS', 'MINUS'],
            'is_prim': True,
            'nets': [],
            'out_terms': [],
            'props': {
                'c': [3, ''],
                'l': [3, ''],
                'm': [3, ''],
                'w': [3, ''],
            }
        },
        'cccs': {
            'lib_name': 'analogLib',
            'cell_name': 'cccs',
            'in_terms': [],
            'io_terms': ['PLUS', 'MINUS'],
            'is_prim': True,
            'nets': [],
            'out_terms': [],
            'props': {
                'fgain': [3, '1.0'],
                'maxm': [3, ''],
                'minm': [3, ''],
                'vref': [3, ''],
            }
        },
        'ccvs': {
            'lib_name': 'analogLib',
            'cell_name': 'ccvs',
            'in_terms': [],
            'io_terms': ['PLUS', 'MINUS'],
            'is_prim': True,
            'nets': [],
            'out_terms': [],
            'props': {
                'hgain': [3, '1.0'],
                'maxm': [3, ''],
                'minm': [3, ''],
                'vref': [3, ''],
            }
        },
        'dcblock': {
            'lib_name': 'analogLib',
            'cell_name': 'dcblock',
            'in_terms': [],
            'io_terms': ['PLUS', 'MINUS'],
            'is_prim': True,
            'nets': [],
            'out_terms': [],
            'props': {
                'c': [3, ''],
            }
        },
        'dcfeed': {
            'lib_name': 'analogLib',
            'cell_name': 'dcfeed',
            'in_terms': [],
            'io_terms': ['PLUS', 'MINUS'],
            'is_prim': True,
            'nets': [],
            'out_terms': [],
            'props': {
                'l': [3, ''],
            }
        },
        'idc': {
            'lib_name': 'analogLib',
            'cell_name': 'idc',
            'in_terms': [],
            'io_terms': ['PLUS', 'MINUS'],
            'is_prim': True,
            'nets': [],
            'out_terms': [],
            'props': {
                'acm': [3, ''],
                'acp': [3, ''],
                'idc': [3, ''],
                'pacm': [3, ''],
                'pacp': [3, ''],
                'srcType': [3, 'dc'],
                'xfm': [3, ''],
            }
        },
        'ideal_balun': {
            'lib_name': 'analogLib',
            'cell_name': 'ideal_balun',
            'in_terms': [],
            'io_terms': ['d', 'c', 'p', 'n'],
            'is_prim': True,
            'nets': [],
            'out_terms': [],
            'props': {}
        },
        'ind': {
            'lib_name': 'analogLib',
            'cell_name': 'ind',
            'in_terms': [],
            'io_terms': ['PLUS', 'MINUS'],
            'is_prim': True,
            'nets': [],
            'out_terms': [],
            'props': {
                'l': [3, ''],
                'm': [3, ''],
                'r': [3, ''],
            }
        },
        'iprobe': {
            'lib_name': 'analogLib',
            'cell_name': 'iprobe',
            'in_terms': [],
            'io_terms': ['PLUS', 'MINUS'],
            'is_prim': True,
            'nets': [],
            'out_terms': [],
            'props': {}
        },
        'ipulse': {
            'lib_name': 'analogLib',
            'cell_name': 'ipulse',
            'in_terms': [],
            'io_terms': ['PLUS', 'MINUS'],
            'is_prim': True,
            'nets': [],
            'out_terms': [],
            'props': {
                'i1': [3, ''],
                'i2': [3, ''],
                'idc': [3, ''],
                'per': [3, ''],
                'pw': [3, ''],
                'srcType': [3, 'pulse'],
                'td': [3, ''],
            }
        },
        'isin': {
            'lib_name': 'analogLib',
            'cell_name': 'isin',
            'in_terms': [],
            'io_terms': ['PLUS', 'MINUS'],
            'is_prim': True,
            'nets': [],
            'out_terms': [],
            'props': {
                'freq': [3, ''],
                'ia': [3, ''],
                'idc': [3, ''],
                'srcType': [3, 'sine'],
            }
        },
        'gnd': {
            'lib_name': 'analogLib',
            'cell_name': 'gnd',
            'in_terms': [],
            'io_terms': ['gnd!'],
            'is_prim': True,
            'nets': [],
            'out_terms': [],
            'props': {},
            'ignore': True,
        },
        'port': {
            'lib_name': 'analogLib',
            'cell_name': 'port',
            'in_terms': [],
            'io_terms': ['PLUS', 'MINUS'],
            'is_prim': True,
            'nets': [],
            'out_terms': [],
            'props': {
                'num': [3, ''],
                'r': [3, ''],
                'srcType': [3, 'sine'],
            }
        },
        'res': {
            'lib_name': 'analogLib',
            'cell_name': 'res',
            'in_terms': [],
            'io_terms': ['PLUS', 'MINUS'],
            'is_prim': True,
            'nets': [],
            'out_terms': [],
            'props': {
                'l': [3, ''],
                'm': [3, ''],
                'r': [3, ''],
                'w': [3, ''],
            }
        },
        'switch': {
            'lib_name': 'analogLib',
            'cell_name': 'switch',
            'in_terms': [],
            'io_terms': ['N+', 'N-', 'NC+', 'NC-'],
            'is_prim': True,
            'nets': [],
            'out_terms': [],
            'props': {
                'rc': [3, ''],
                'ro': [3, ''],
                'vt1': [3, ''],
                'vt2': [3, ''],
            }
        },
        'vccs': {
            'lib_name': 'analogLib',
            'cell_name': 'vccs',
            'in_terms': [],
            'io_terms': ['PLUS', 'MINUS', 'NC+', 'NC-'],
            'is_prim': True,
            'nets': [],
            'out_terms': [],
            'props': {
                'ggain': [3, '1.0'],
                'maxm': [3, ''],
                'minm': [3, ''],
            }
        },
        'vcvs': {
            'lib_name': 'analogLib',
            'cell_name': 'vcvs',
            'in_terms': [],
            'io_terms': ['PLUS', 'MINUS', 'NC+', 'NC-'],
            'is_prim': True,
            'nets': [],
            'out_terms': [],
            'props': {
                'egain': [3, '1.0'],
                'maxm': [3, ''],
                'minm': [3, ''],
            }
        },
        'vdc': {
            'lib_name': 'analogLib',
            'cell_name': 'vdc',
            'in_terms': [],
            'io_terms': ['PLUS', 'MINUS'],
            'is_prim': True,
            'nets': [],
            'out_terms': [],
            'props': {
                'acm': [3, ''],
                'acp': [3, ''],
                'pacm': [3, ''],
                'pacp': [3, ''],
                'srcType': [3, 'dc'],
                'vdc': [3, ''],
                'xfm': [3, ''],
            }
        },
        'vpulse': {
            'lib_name': 'analogLib',
            'cell_name': 'vpulse',
            'in_terms': [],
            'io_terms': ['PLUS', 'MINUS'],
            'is_prim': True,
            'nets': [],
            'out_terms': [],
            'props': {
                'per': [3, ''],
                'pw': [3, ''],
                'srcType': [3, 'pulse'],
                'td': [3, ''],
                'v1': [3, ''],
                'v2': [3, ''],
                'vdc': [3, ''],
            }
        },
        'vpwlf': {
            'lib_name': 'analogLib',
            'cell_name': 'vpwlf',
            'in_terms': [],
            'io_terms': ['PLUS', 'MINUS'],
            'is_prim': True,
            'nets': [],
            'out_terms': [],
            'props': {
                'fileName': [3, ''],
                'srcType': [3, 'pwl'],
            }
        },
        'vsin': {
            'lib_name': 'analogLib',
            'cell_name': 'vsin',
            'in_terms': [],
            'io_terms': ['PLUS', 'MINUS'],
            'is_prim': True,
            'nets': [],
            'out_terms': [],
            'props': {
                'freq': [3, ''],
                'srcType': [3, 'sine'],
                'va': [3, ''],
                'vdc': [3, ''],
            }
        },
    },
}

mos_default = {
    'lib_name': 'BAG_prim',
    'cell_name': '',
    'in_terms': [],
    'out_terms': [],
    'io_terms': ['B', 'D', 'G', 'S'],
    'nets': [],
    'is_prim': True,
    'props': {
        'l': [3, ''],
        'w': [3, ''],
        'nf': [3, ''],
    },
}

dio_default = {
    'lib_name': 'BAG_prim',
    'cell_name': '',
    'in_terms': [],
    'out_terms': [],
    'io_terms': ['MINUS', 'PLUS'],
    'nets': [],
    'is_prim': True,
    'props': {
        'l': [3, ''],
        'w': [3, ''],
    },
}

res_metal_default = {
    'lib_name': 'BAG_prim',
    'cell_name': '',
    'in_terms': [],
    'out_terms': [],
    'io_terms': ['MINUS', 'PLUS'],
    'nets': [],
    'is_prim': True,
    'props': {
        'l': [3, ''],
        'w': [3, ''],
    },
}

mos_cdl_fmt = """.SUBCKT {{ cell_name }} B D G S
*.PININFO B:B D:B G:B S:B
MM0 D G S B {{ model_name }}{% for key, val in param_list %} {{ key }}={{ val }}{% endfor %}
.ENDS
"""

dio_cdl_fmt = """.SUBCKT {{ cell_name }} MINUS PLUS
*.PININFO MINUS:B PLUS:B
XD0 {{ ports[0] }} {{ ports[1] }} {{ model_name }}{% for key, val in param_list %} {{ key }}={{ val }}{% endfor %}
.ENDS
"""

dio_cdl_fmt_static = """.SUBCKT {{ cell_name }} MINUS PLUS
*.PININFO MINUS:B PLUS:B
XD0 {{ ports[0] }} {{ ports[1] }} {{ model_name }}
.ENDS
"""

res_metal_cdl_fmt = """.SUBCKT {{ cell_name }} MINUS PLUS
*.PININFO MINUS:B PLUS:B
RR0 PLUS MINUS {{ model_name }} {% for key, val in param_list %} {{ key }}={{ val }}{% endfor %}
.ENDS
"""

mos_spectre_fmt = """subckt {{ cell_name }} B D G S
parameters l w nf
MM0 D G S B {{ model_name }}{% for key, val in param_list %} {{ key }}={{ val }}{% endfor %}
ends {{ cell_name }}
"""

dio_spectre_fmt = """subckt {{ cell_name }} MINUS PLUS
parameters l w
XD0 {{ ports[0] }} {{ ports[1] }} {{ model_name }}{% for key, val in param_list %} {{ key }}={{ val }}{% endfor %}
ends {{ cell_name }}
"""

dio_spectre_fmt_static = """subckt {{ cell_name }} MINUS PLUS
parameters l w
XD0 {{ ports[0] }} {{ ports[1] }} {{ model_name }}
ends {{ cell_name }}
"""

res_metal_spectre_fmt = """subckt {{ cell_name }} MINUS PLUS
parameters l w
RR0 PLUS MINUS {{ model_name }} {% for key, val in param_list %} {{ key }}={{ val }}{% endfor %}
ends {{ cell_name }}
"""

mos_verilog_fmt = """module {{ cell_name }}(
    inout B,
    inout D,
    inout G,
    inout S
);
endmodule
"""

scs_ideal_balun = """subckt ideal_balun d c p n
    K0 d 0 p c transformer n1=2
    K1 d 0 c n transformer n1=2
ends ideal_balun
"""

supported_formats = {
    DesignOutput.CDL: {
        'fname': 'bag_prim.cdl',
        'mos': 'mos_cdl',
        'diode': 'diode_cdl',
        'diode_static': 'diode_cdl_static',
        'res_metal': 'res_metal_cdl',
    },
    DesignOutput.SPECTRE: {
        'fname': 'bag_prim.scs',
        'mos': 'mos_scs',
        'diode': 'diode_scs',
        'diode_static': 'diode_scs_static',
        'res_metal': 'res_metal_scs',
    },
    DesignOutput.VERILOG: {
        'fname': 'bag_prim.v',
        'mos': '',
        'diode': '',
        'diode_static': '',
        'res_metal': '',
    },
    DesignOutput.SYSVERILOG: {
        'fname': 'bag_prim.sv',
        'mos': '',
        'diode': '',
        'diode_static': '',
        'res_metal': '',
    },
}

jinja_env = Environment(
    loader=DictLoader(
        {'mos_cdl': mos_cdl_fmt,
         'mos_scs': mos_spectre_fmt,
         'mos_verilog': mos_verilog_fmt,
         'diode_cdl': dio_cdl_fmt,
         'diode_scs': dio_spectre_fmt,
         'diode_cdl_static': dio_cdl_fmt_static,
         'diode_scs_static': dio_spectre_fmt_static,
         'res_metal_cdl': res_metal_cdl_fmt,
         'res_metal_scs': res_metal_spectre_fmt}),
    keep_trailing_newline=True,
)


def populate_header(config: Dict[str, Any], inc_lines: Dict[DesignOutput, List[str]],
                    inc_list: Dict[int, List[str]]) -> None:
    for v, lines in inc_lines.items():
        inc_list[v.value] = config[v.name]['includes']


def populate_mos(config: Dict[str, Any], netlist_map: Dict[str, Any],
                 inc_lines: Dict[DesignOutput, List[str]]) -> None:
    for cell_name, model_name in config['types']:
        # populate netlist_map
        cur_info = copy.deepcopy(mos_default)
        cur_info['cell_name'] = cell_name
        netlist_map[cell_name] = cur_info

        # write bag_prim netlist
        for v, lines in inc_lines.items():
            param_list = config[v.name]
            template_name = supported_formats[v]['mos']
            if template_name:
                mos_template = jinja_env.get_template(template_name)
                lines.append('\n')
                lines.append(
                    mos_template.render(
                        cell_name=cell_name,
                        model_name=model_name,
                        param_list=param_list,
                    ))


def populate_diode(config: Dict[str, Any], netlist_map: Dict[str, Any],
                   inc_lines: Dict[DesignOutput, List[str]]) -> None:
    template_key = 'diode_static' if config['static'] else 'diode'

    for cell_name, model_name in config['types']:
        # populate netlist_map
        cur_info = copy.deepcopy(dio_default)
        cur_info['cell_name'] = cell_name
        netlist_map[cell_name] = cur_info
        ports = config['port_order'][cell_name]

        # write bag_prim netlist
        for v, lines in inc_lines.items():
            param_list = config[v.name]
            template_name = supported_formats[v][template_key]
            if template_name:
                jinja_template = jinja_env.get_template(template_name)
                lines.append('\n')
                lines.append(
                    jinja_template.render(
                        cell_name=cell_name,
                        model_name=model_name,
                        ports=ports,
                        param_list=param_list,
                    ))


def populate_res_metal(config: Dict[str, Any], netlist_map: Dict[str, Any],
                       inc_lines: Dict[DesignOutput, List[str]]) -> None:
    for idx, (cell_name, model_name) in enumerate(config['types']):
        # populate netlist_map
        cur_info = copy.deepcopy(res_metal_default)
        cur_info['cell_name'] = cell_name
        netlist_map[cell_name] = cur_info

        # write bag_prim netlist
        for v, lines in inc_lines.items():
            param_list = config[v.name]
            template_name = supported_formats[v]['res_metal']
            write_res_val = config.get('write_res_val', False)
            new_param_list = param_list.copy()
            if write_res_val:
                res_val = config['res_map'][idx + 1]
                new_param_list.append(['r', '{}*l/w'.format(res_val)])
            if template_name:
                res_metal_template = jinja_env.get_template(template_name)
                lines.append('\n')
                lines.append(
                    res_metal_template.render(
                        cell_name=cell_name,
                        model_name=model_name,
                        param_list=new_param_list,
                    ))


def populate_custom_cells(inc_lines: Dict[DesignOutput, List[str]]):
    scs_lines = inc_lines[DesignOutput.SPECTRE]
    scs_lines.append('\n')
    scs_lines.append(scs_ideal_balun)


def get_info(config: Dict[str, Any], output_dir: Path
             ) -> Tuple[Dict[str, Any], Dict[int, List[str]], Dict[int, str]]:
    netlist_map = {}
    inc_lines = {v: [] for v in supported_formats}

    inc_list: Dict[int, List[str]] = {}
    populate_header(config['header'], inc_lines, inc_list)
    populate_mos(config['mos'], netlist_map, inc_lines)
    populate_diode(config['diode'], netlist_map, inc_lines)
    populate_res_metal(config['res_metal'], netlist_map, inc_lines)
    populate_custom_cells(inc_lines)

    prim_files: Dict[int, str] = {}
    for v, lines in inc_lines.items():
        fpath = output_dir / supported_formats[v]['fname']
        if lines:
            prim_files[v.value] = str(fpath)
            with open_file(fpath, 'w') as f:
                f.writelines(lines)
        else:
            prim_files[v.value] = ''

    return {'BAG_prim': netlist_map}, inc_list, prim_files


def parse_options() -> Tuple[str, Path]:
    parser = argparse.ArgumentParser(description='Generate netlist setup file.')
    parser.add_argument(
        'config_fname', type=str, help='YAML file containing technology information.')
    parser.add_argument('output_dir', type=str, help='Output directory.')
    args = parser.parse_args()
    return args.config_fname, Path(args.output_dir)


def main() -> None:
    config_fname, output_dir = parse_options()

    output_dir.mkdir(parents=True, exist_ok=True)

    config = read_yaml(config_fname)

    netlist_map, inc_list, prim_files = get_info(config, output_dir)
    netlist_map.update(netlist_map_default)
    result = {
        'prim_files': prim_files,
        'inc_list': inc_list,
        'netlist_map': netlist_map,
    }

    write_yaml(output_dir / 'netlist_setup.yaml', result)


if __name__ == '__main__':
    main()
