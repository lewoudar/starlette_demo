"""added snippet model

Revision ID: e41421b8ad26
Revises: 9cf0a18a66da
Create Date: 2020-06-28 10:50:11.929268

"""
from alembic import op
import sqlalchemy_utils
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e41421b8ad26'
down_revision = '9cf0a18a66da'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('snippets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('code', sa.Text(), nullable=False),
    sa.Column('linenos', sa.Boolean(), nullable=False),
    sa.Column('language', sa.Enum('abap', 'abnf', 'ada', 'adl', 'agda', 'aheui', 'ahk', 'alloy', 'ampl', 'antlr', 'antlr-as', 'antlr-cpp', 'antlr-csharp', 'antlr-java', 'antlr-objc', 'antlr-perl', 'antlr-python', 'antlr-ruby', 'apacheconf', 'apl', 'applescript', 'arduino', 'as', 'as3', 'aspectj', 'aspx-cs', 'aspx-vb', 'asy', 'at', 'augeas', 'autoit', 'awk', 'basemake', 'bash', 'bat', 'bbcbasic', 'bbcode', 'bc', 'befunge', 'bib', 'blitzbasic', 'blitzmax', 'bnf', 'boa', 'boo', 'boogie', 'brainfuck', 'bst', 'bugs', 'c', 'c-objdump', 'ca65', 'cadl', 'camkes', 'capdl', 'capnp', 'cbmbas', 'ceylon', 'cfc', 'cfengine3', 'cfm', 'cfs', 'chai', 'chapel', 'charmci', 'cheetah', 'cirru', 'clay', 'clean', 'clojure', 'clojurescript', 'cmake', 'cobol', 'cobolfree', 'coffee-script', 'common-lisp', 'componentpascal', 'console', 'control', 'coq', 'cpp', 'cpp-objdump', 'cpsa', 'cr', 'crmsh', 'croc', 'cryptol', 'csharp', 'csound', 'csound-document', 'csound-score', 'css', 'css+django', 'css+erb', 'css+genshitext', 'css+lasso', 'css+mako', 'css+mozpreproc', 'css+myghty', 'css+php', 'css+smarty', 'cucumber', 'cuda', 'cypher', 'cython', 'd', 'd-objdump', 'dart', 'dasm16', 'delphi', 'dg', 'diff', 'django', 'docker', 'doscon', 'dpatch', 'dtd', 'duel', 'dylan', 'dylan-console', 'dylan-lid', 'earl-grey', 'easytrieve', 'ebnf', 'ec', 'ecl', 'eiffel', 'elixir', 'elm', 'emacs', 'email', 'erb', 'erl', 'erlang', 'evoque', 'extempore', 'ezhil', 'factor', 'fan', 'fancy', 'felix', 'fennel', 'fish', 'flatline', 'floscript', 'forth', 'fortran', 'fortranfixed', 'foxpro', 'freefem', 'fsharp', 'gap', 'gas', 'genshi', 'genshitext', 'glsl', 'gnuplot', 'go', 'golo', 'gooddata-cl', 'gosu', 'groff', 'groovy', 'gst', 'haml', 'handlebars', 'haskell', 'haxeml', 'hexdump', 'hlsl', 'hsail', 'hspec', 'html', 'html+cheetah', 'html+django', 'html+evoque', 'html+genshi', 'html+handlebars', 'html+lasso', 'html+mako', 'html+myghty', 'html+ng2', 'html+php', 'html+smarty', 'html+twig', 'html+velocity', 'http', 'hx', 'hybris', 'hylang', 'i6t', 'icon', 'idl', 'idris', 'iex', 'igor', 'inform6', 'inform7', 'ini', 'io', 'ioke', 'irc', 'isabelle', 'j', 'jags', 'jasmin', 'java', 'javascript+mozpreproc', 'jcl', 'jlcon', 'js', 'js+cheetah', 'js+django', 'js+erb', 'js+genshitext', 'js+lasso', 'js+mako', 'js+myghty', 'js+php', 'js+smarty', 'jsgf', 'json', 'json-object', 'jsonld', 'jsp', 'julia', 'juttle', 'kal', 'kconfig', 'kmsg', 'koka', 'kotlin', 'lagda', 'lasso', 'lcry', 'lean', 'less', 'lhs', 'lidr', 'lighty', 'limbo', 'liquid', 'live-script', 'llvm', 'llvm-mir', 'llvm-mir-body', 'logos', 'logtalk', 'lsl', 'lua', 'make', 'mako', 'maql', 'mask', 'mason', 'mathematica', 'matlab', 'matlabsession', 'md', 'mime', 'minid', 'modelica', 'modula2', 'monkey', 'monte', 'moocode', 'moon', 'mosel', 'mozhashpreproc', 'mozpercentpreproc', 'mql', 'ms', 'mscgen', 'mupad', 'mxml', 'myghty', 'mysql', 'nasm', 'ncl', 'nemerle', 'nesc', 'newlisp', 'newspeak', 'ng2', 'nginx', 'nim', 'nit', 'nixos', 'notmuch', 'nsis', 'numpy', 'nusmv', 'objdump', 'objdump-nasm', 'objective-c', 'objective-c++', 'objective-j', 'ocaml', 'octave', 'odin', 'ooc', 'opa', 'openedge', 'pacmanconf', 'pan', 'parasail', 'pawn', 'peg', 'perl', 'perl6', 'php', 'pig', 'pike', 'pkgconfig', 'plpgsql', 'pony', 'postgresql', 'postscript', 'pot', 'pov', 'powershell', 'praat', 'prolog', 'properties', 'protobuf', 'ps1con', 'psql', 'pug', 'puppet', 'py2tb', 'pycon', 'pypylog', 'pytb', 'python', 'python2', 'qbasic', 'qml', 'qvto', 'racket', 'ragel', 'ragel-c', 'ragel-cpp', 'ragel-d', 'ragel-em', 'ragel-java', 'ragel-objc', 'ragel-ruby', 'raw', 'rb', 'rbcon', 'rconsole', 'rd', 'reason', 'rebol', 'red', 'redcode', 'registry', 'resource', 'rexx', 'rhtml', 'ride', 'rnc', 'roboconf-graph', 'roboconf-instances', 'robotframework', 'rql', 'rsl', 'rst', 'rts', 'rust', 'sarl', 'sas', 'sass', 'sc', 'scala', 'scaml', 'scdoc', 'scheme', 'scilab', 'scss', 'sgf', 'shen', 'shexc', 'sieve', 'silver', 'slash', 'slim', 'slurm', 'smali', 'smalltalk', 'smarty', 'sml', 'snobol', 'snowball', 'solidity', 'sourceslist', 'sp', 'sparql', 'spec', 'splus', 'sql', 'sqlite3', 'squidconf', 'ssp', 'stan', 'stata', 'swift', 'swig', 'systemverilog', 'tads3', 'tap', 'tasm', 'tcl', 'tcsh', 'tcshcon', 'tea', 'termcap', 'terminfo', 'terraform', 'tex', 'text', 'thrift', 'todotxt', 'toml', 'trac-wiki', 'treetop', 'ts', 'tsql', 'ttl', 'turtle', 'twig', 'typoscript', 'typoscriptcssdata', 'typoscripthtmldata', 'ucode', 'unicon', 'urbiscript', 'usd', 'vala', 'vb.net', 'vbscript', 'vcl', 'vclsnippets', 'vctreestatus', 'velocity', 'verilog', 'vgl', 'vhdl', 'vim', 'wdiff', 'webidl', 'whiley', 'x10', 'xml', 'xml+cheetah', 'xml+django', 'xml+erb', 'xml+evoque', 'xml+lasso', 'xml+mako', 'xml+myghty', 'xml+php', 'xml+smarty', 'xml+velocity', 'xorg.conf', 'xquery', 'xslt', 'xtend', 'xul+mozpreproc', 'yaml', 'yaml+jinja', 'zeek', 'zephir', 'zig', name='language'), nullable=False),
    sa.Column('style', sa.Enum('abap', 'algol', 'algol_nu', 'arduino', 'autumn', 'borland', 'bw', 'colorful', 'default', 'emacs', 'friendly', 'fruity', 'igor', 'inkpot', 'lovelace', 'manni', 'monokai', 'murphy', 'native', 'paraiso-dark', 'paraiso-light', 'pastie', 'perldoc', 'rainbow_dash', 'rrt', 'sas', 'solarized-dark', 'solarized-light', 'stata', 'stata-dark', 'stata-light', 'tango', 'trac', 'vim', 'vs', 'xcode', name='style'), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_snippets_user_id_users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_snippets'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('snippets')
    # ### end Alembic commands ###
