# This file exists within 'dob':
#
#   https://github.com/hotoffthehamster/dob
#
# Copyright © 2018-2020 Landon Bouma,  2015-2016 Eric Goller.  All rights reserved.
#
# 'dob' is free software: you can redistribute it and/or modify it under the terms
# of the GNU General Public License  as  published by the Free Software Foundation,
# either version 3  of the License,  or  (at your option)  any   later    version.
#
# 'dob' is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY  or  FITNESS FOR A PARTICULAR
# PURPOSE.  See  the  GNU General Public License  for  more details.
#
# You can find the GNU General Public License reprinted in the file titled 'LICENSE',
# or visit <http://www.gnu.org/licenses/>.

import os
import random

from gettext import gettext as _

import click

from .emphasis import attr, bg, fg

try:
    # (lb): Not including pyfiglet because it's large and unnecessary.
    from pyfiglet import Figlet
except ImportError:
    pass


__all__ = (
    'hamster_artwork',
    'fingies_artwork',
    'fetch_asciis',
    'randomster',
    'lifeless',
    'infection_notice',
    'curly_quote',
    'curly_quotes',
)

# (lb): Disable E501 line too long. Or, really,
# ignore the whole file; that's the only choice.
# flake8: noqa


def hamster_artwork():
    """Hamster Litter."""
    hamster_artwork = [
        _hamster_artwork_01,
        _hamster_artwork_02,
        _hamster_artwork_03,
        _hamster_artwork_04,
        _hamster_artwork_05,
        _hamster_artwork_06,
        _hamster_artwork_07,
        _hamster_artwork_08,
        _hamster_artwork_09,
        _hamster_artwork_10,
        _hamster_artwork_11,
    ]
    # Add randomized font image, but make less likely.
    artwork = hamster_artwork * 3
    append_figlet_text_maybe(artwork)
    return artwork


def fingies_artwork():
    """Real Art!"""
    fingies_artwork = [
        middle_fingie_01,
        # middle_fingie_02_copy_of_01_with_ellipses,  # disabled; quasi-duplicate.
        middle_fingie_03,
        middle_fingie_04,
        middle_fingie_05,
    ]
    return fingies_artwork


def dead_hamsters_society():
    """Tune in, turn on, and drop dead."""
    defunct_artwork = [
        _hamster_corpse_01,
        # _hamster_corpse_02,  # disabled; a smaller _hamster_corpse_03.
        _hamster_corpse_03,
        _hamster_corpse_04,
        _hamster_corpse_05,
        # _hamster_corpse_06,  # disabled; a smaller _hamster_corpse_05.
        _hamster_corpse_07,
        # _hamster_corpse_08,  # disabled; a larger _hamster_corpse_07.
        _hamster_corpse_09,
        # _hamster_corpse_10,  # disabled; cannot tell what it is!
    ]
    return defunct_artwork


def append_figlet_text_maybe(artwork):
    try:
        artwork.append(figletize_hamster())
    except Exception as err:
        return


def figletize_hamster():
    figlet = Figlet()
    figlet.setFont(font=random.choice(figlet.getFonts()))
    hword = ''.join(
        random.choice(
            (str.upper, str.lower)
        )(lttr) for lttr in 'hamster'
    )
    rendered = figlet.renderText(hword)
    return "\n" + rendered + "\n"


def infection_notice():
    return _infection_notice


# ***

_hamster_artwork_01 = (
    '''
            (>\\---/<)
            ,'     `.
           /  q   p  \\
          (  >(_Y_)<  )
           >-' `-' `-<-.
          /  _.== ,=.,- \\
         /,    )`  '(    )
        ; `._.'      `--<
       :     \\        |  )
       \\      )       ;_/  hjw
        `._ _/_  ___.'-\\\\\\
           `--\\\\\\

''')
# http://ascii.co.uk/art/hamster

_hamster_artwork_02 = (
    '''
          _           _
        (`-`;-"```"-;`-`)
         \\.'         './
         /             \\
         ;   0     0   ;
        /| =         = |\\
       ; \\   '._Y_.'   / ;
      ;   `-._ {}{}\\|/{} _.-'   ;
     ;        `"""`        ;
     ;    `""-.   .-""`    ;
     /;  '--._ \\ / _.--   ;\\
    :  `.   `/|| ||\\`   .'  :
     '.  '-._       _.-'   .'
 jgs (((-'`  `"""""`   `'-)))

'''.format(bg('yellow'), fg('black'), attr('reset')))
# http://ascii.co.uk/art/hamster


_hamster_artwork_02_colorful = (
    '''
{}          _           _
{}        (`-`;-"```"-;`-`)
{}         \\.'         './
{}         /             \\
{}         ;   0     0   ;
{}        /| =         = |\\
{}       ; \\   '._Y_.'   / ;
{}      ;   `-._ {}{}\\|/{} _.-'   ;
{}     ;        `"""`        ;
{}     ;    `""-.   .-""`    ;
{}     /;  '--._ \\ / _.--   ;\\
{}    :  `.   `/|| ||\\`   .'  :
{}     '.  '-._       _.-'   .'
{}     (((-'`  `"""""`   `'-)))

'''.format(
        fg(90), fg(91), fg(92), fg(93), fg(100), fg(101), fg(102), fg(103),
        bg('yellow'), fg('black'), attr('reset'),
        fg(103),
        fg(104), fg(105), fg(106), fg(107), fg(108), fg(109), fg(110),
        attr('reset'),
    ))
# http://ascii.co.uk/art/hamster


_hamster_artwork_03 = (
    #    '''
    #            o_
    #         .-"  ".
    #       ."    _-'-""--o
    #      J    ,"" _      ".
    #   .-",___,)____)___),-'
    #
    '''
            o_
         .-"  ".
       ."    _-'-""--o
      J    {}@{}={}" _      ".
   .-",___,)____)___),-'

'''.format(fg('purple_4a'), fg('purple_4a'), attr('reset')))
# Title: "Hamster Style" - by gla
# Credit: bmw

# MAYBE/2018-05-16: (lb): (This isn't branding.)
#   Find other banners using different fonts to make that point clear.
_hamster_artwork_04 = (
    '''
{}888                                  888
{}888                                  888
{}888                                  888
{}88888b.  8888b. 88888b.d88b. .d8888b 888888 .d88b. 888d888
{}888 "88b    "88b888 "888 "88b88K     888   d8P  Y8b888P"
{}888  888.d888888888  888  888"Y8888b.888   88888888888
{}888  888888  888888  888  888     X88Y88b. Y8b.    888
{}888  888"Y888888888  888  888 88888P' "Y888 "Y8888 888
{}
'''.format(
        fg(90), fg(91), fg(92), fg(93), fg(100), fg(101), fg(102), fg(103),
        attr('reset'),
    ))

_hamster_artwork_05 = (
    '''
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMXKWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMXx::lkK0xkXWMMMMMMMMMMMN0XMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMWNNXK00000KN0c;;;:;,::;co0WWXK0XNWWOolod0NMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMXkdocclc:;;;;;:l,....'.',,;c::ddc;;clkKddl:c:kWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMW0o:,:lloooooooolc,':c;,,,,':c:,.:dc'.,c:,,c:,c:codkO0XWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMWk;:odxxdooooodl,;,  ,lcc:::::;..,:lc::clc;:ooodxxocllclxKWMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMM0clxlcdkxxxxxxk:  ...:llc::::::;..',;:;cdkkxxxxxkOkkkkkkdodONMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMk,:lldOkxxxxxxko;',;coool:::cc:;'..cllllddxxxxkOddc,lxkkkkxodONMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMO:oKNNNXOxxxxxxxxdddddooollcc:;;..:loxxxxxxkkxOdcl. .lxxkkkkxodONMMMMMMMMMMMXk0WMMMMMMM
MMMMMMMMMMMMMMMMMNxoXWWWWKOkxxdddodddooolll:;:c:,.;odxkOkkkkkkxko'. ..:xxkkkkkkxldNMMMMMMMMN0xodOXMMMMMM
MMMMMMMMMMMMMMMMMMNdo0WWWWNX0Oxxdodk0KK0xl;,,:c:..codxxxxkkOOkxxxc;;,:dxkkxkkkkkdckMMMMMMMW0ddxxol0MMMMM
MMMMMMMMMMMMMMMMMMMW0xkOKNWNWWNNNXXNNOdc'.':lccc''lodxxxkkkkkkkxxkkxxxxkkkkxxkkOxckMWWWWWNOxkKWXdlKMMMMM
MMMMMMMMMMMMMMMMMMMMMWXx;,:coxdddol;,,,;cloooolc,'codxkOOkO00K0OOkOOkkkxkOdoc:okx:xOlcclolc:xNMMWWMMMMMM
MMMMMMMMMMMMMMMMMMMMMMXo;coddxdlcccoxOxxOkdddooc'.:lodxxkO00k0NNXXK000K0O0KNXxcc:;dl::,..'',:kWMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMNkloOKXNWWWMMWWXxlkX0o:d0kdc''coodxxkKNNKOkkxk0XWWWWWWWNNWNk';0kldxocc::;dWMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMkoxkXWWWWWWMNKxldKN0c'cONKd;.,lodxxkkk0NXKNNKkkxxk0000OkOxl,..cx:;lc:;:;oXMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMKdOk;c0WWMMKocooON0l:l0NNKko;.:oodxkkkoxOllk0KXNNKOxxocc:;:::l:,::cOx;coc0MMMMMMMMMMM
MMMMMMMMMMMMMMMMMMM0oko.cXMMMMKx:'lxd;:0WWKkxdo'.:loxkkkxokd:okkOOKNWWMMWWNNNNNXXXx;':kx,;cdXMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMWO:,ckNMMMMMXxl:','cXWWNK0Ok;.;oodxxkxoOx;oO0KNNWMMMMMMMMMMWWMWWKc.cl;ckNMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMNWMMx'dWWMMMMMMWM0d0K0NWWWMWWWo..codxxdlcxKo:dKNWWWWMWMMMMMMMMWWMWW0:l0Ox0WMMMMMMMMMMMM
MMMMMMMMMMMMMMWN0x0WMXl:0NWMMNNMMMMWWWMWNXNWMMNO'.;loddo:cdl:;,:k000XNWMMMWWWMWWWWWWXc;do;dNWWMMWWMMMMMM
MMMMMMMMMMMWWMWNNXKNMNo'o0NWMNXWWko0XKNNKkkxO0ko,..':odddl::,:ddxOO0XWMMMMWWMMWWMWNWO'.odcOWWWWK0WMMMMMM
MMMMMMMMMMMMMMMWWO:ldccxxod0NNKX0oodxxolloodddoc'.  .:ldddxxxxxxkOO0XWWNNWMWWWNKXNKO:.;xccKWWWO;'dNWMMMM
MMMMMMMMMMMMMXXWW0llddkd;'';ll:lo:x0o:cdxxooc;,'... ...',coddxxdxxkkkOKKOx0NN0kolxl,,cllldKNWWNOoxNWMMMM
MMMMMMMMMMMNx:cokNXdloolx0K0Oxl:,.,OX0Oko:,;;;;:clllc:,''.'',clloddxkkO0K0doxoko.':d0XXNNNNWWWMMMMMMMMMM
MMMMMMMMMMWKo:ldONWWXXNNKkdddloO0xclddoooxkkO0KKXNNXKKXK0kl;:c;,;;;:ccloxOkdodx;,d0XWWWWWWWMMMMMWNWMMMMM
MMMMMMMMMMWNXXWMMMMMWWWkldkko;':OXKXXNWWWWMWNKk0WMWWWWWMMMWNXNXOOxdxxolllccclol;o0NWWXxllldOXWWMWXWMMMMM
MMMMMMMMMMMMWNWMMMMMWXX0xdoc;cc;xNWWMMMWMMWXkl;cOWWMWXXWWWNOdONWWNNNWWNNXKKOxdxk0XNWWk,;lc'.'oXWWMMMMMMM
MMMMMMMMMMMMWXWMMMMMMNWWWNXd:::l0NNWMMMNNMWX0dod0NNWXdkNNKd,;;:kWMNXNWWWMMMNNNWWWWNNWXd:c::ccdKNWWMMMMMM
MMMMMMMMMMMMMMMMMMMMMWMMWWWk:oOXNWWMMMMWWMMMWWWMMWWMMWWMO:codxo:kWNNWMMMMMMMWWWMMMMWWWNXKXNXXXNWWWMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMNXNWMMWMMMMMMMMMMMMMMMMWMWN0kodkcl0WXXWMMMMMWWMMMMMMMMMMMMMMWWMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWWWNOxooxl;kWWWMWWMMWWMMMMMMMMMMMWWMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWMWNXX0xdOWMWWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM

''')
# https://jelbo.deviantart.com/art/Sitting-Hamsters-48120570
# https://www.ascii-art-generator.org/

_hamster_artwork_06 = (
    '''
                                        ..
                                      .;ddl,..;,.             ..
                            ........ 'okxxdxkddxoc.  ....   'clc;.
                     .,:cooloxxxxxxdlk00XKO0Okkxodd::oxxol,.::lxod,
                   .cdkdllcccccccllokOdoxkkkOOxodk0d:d0Kkoxkkodkodoc:,'..
                  ,xdc:;;:ccccc:lkxkNNkloddddddxKKkdloddoldkdccc:;;collol;.
                 .ol;lo:;;;;;;;;dNNXXKdllodddxddx0KOkxdxo:,,;;;;;,',;,,,,cc:'
                 ,kdll:',;;;;;;;cxOkxocccldddoodxOX0ollllc:;;;;,'::okl;,,,,;c:'
                 'dc.   .';;;;;;;;:::::ccllloddxx00dlc;;;;;;;,;':ol0MKl;;,,,,:c:'            .,.
                  ;c.    .,;;::::c:::cccllldxdodk0xc:;,',,,,;,,,cOXNXKd;;,,,,,,;l:          .;c:'.
                   :c.     ..';;:c:,....;lxkkdox00oc:;;;;,,',,;;;okxkd:;;,;,,,,;:o,        '::;;cl.
                    .;,'.        ..  ':oOKOdloooOOoc:;;;;,,,,,,;;,,;;;;;,,;;;,,';o,       ':,. .:l.
                      .:xkdoc;:::clxkOkxolcccclokOoc::,,,,'....',,'',,,;,':codc,;d;'loolclod;
                      .cxoc::;:loooc;,;;',:::ccoO0dlc:;;,'..,.  ....'..'... .;oodx:lddk0KOOkd,
                     ,lc'..        .;l,.'cd:.,:o0Oocc:;;,.  .',,;,..           ,Ox.,l:;cooddx:
                    ,c;,.        .;l:. 'oOd' .:xKklc:;;,,,' ... .,;;;,....',';lkXKo;dxlodxxxc.
                   .:',xo.    .locc' .ldl.  .,cx0dcc:;,,,c;'ll,'..  .';:loodxdddldkddo,;xoco.
                   .c,c0o.    .;dOo;:xd.  .,;:cOKdlc;,,,;c,:dc,,,'.            ...;xOd,;kxo:.
                    'xko,      .:ldOkOo.   ..',kKxlc:;;,;c';xc'..                  .o0olxo,
                     ;O:          .c...        cK0oc:;;:lo;.cx:.                    .dl.';.
                .;.  .ld.                .     'OXxlc::cdo:ldxkd;....               .ox:cx:
                 ..   cOc.    .  ,c...  .,,;'.,ckXXOdc:::lddkxcc;',..               'O0c:o'    ..
                 ,dl:oo;;c:.  ...cc:;;cllcl:::coOXNN0dl:::;;;;;;,''..          .. .'dXx;oo.   'xO:
             ..  .ll::,:xOOxlldlcd;.cdlc;;cloxkOKXXNXX0Okoc::;;:;;,,,'..';.  .,cl:lkkolll:.    'c;
            ;doc, .:lccl:...';ldkKk'..',cdkxkkxdollloxkOO0OOkollc::;,,'...:c:c,c0Odc...
           .cdl:'   ..  .,:::lc'.;ol::ccc;,,,.... .......,lxdoxkxxxddolc;',:c:;xk:..
            ..         ,l:,,cxOd'....        .,.            . .',;::;clloooolclxc.   .,lll:'.    .
                     ...;ccoxoox:          .,lxo'    ..    ':,.         ...';::;..   'kxloO0Oc.
             .            .:dddl.          ..:c:.   .:,  .:kxxd,   ..                .:ddddoo:.
                           ;dc'.                        'doc:;cd;                      ... ...
                            .                         .,c:,ol. ..
                                                      ';cc;lx,
                                                       ...;c'

''')
# https://jelbo.deviantart.com/art/Sitting-Hamsters-48120570
# https://www.ascii-art-generator.org/

_hamster_artwork_07 = (
    """
                        .',,.       . ..
                       ,loooo,    ............
                    ..;olc:;ll...,:'......;,...
                   ..,od:,;cl:;:ldoo:';lllol:,..
         .,''.     ..;doccc:,',:cccclddc:looo;.
        .,co:.    ..;l:',,,,'',;;;,,,co:,:ooc.
         .:oo' .',;lko...''''',,,',,,,cl:ldd,
       ...;oxo,':lol;...;cc;..'''',,,,;cclol'
      .:,';ldxd:cdxdc...;ol;...':c;''''...:o:.
     .:l::ccllllcclod;.........;ol,...'..;dxdc::;.
   .';c:ccclllccoxdoxxd:. ............'';lxkxo;'.
  ...,:::::;lxxxolxxkOkkl;cc...',...'coodxxl;..
 ...........ckkkdldkkkkkO0kollllc,,clodoooc,..
          'codxxkxoooolloollloooo;';lddl::ll;'..
       .,ldxxddxOkoddool:::cloooo:';loc:cddlc;,.
     .;lxxxkkdc;:,,cl,,cc:::c:ccc::cldddolloc;:'
  .,cddxkOOxl;....':oc'....''',cooolllooollol:'.
 'dxdxkOxol;.. .;;';cc:::;:cccoolccc:::;:::;,'.
 .oOOkko::'.    'lc:llcolccllool:,;;,;:;,,'...
  .x00kl,.      ,doc:::clllc::;;;;;'  .. ..
   'lc'        .lxdlll::c:::;:::,'...''.
              'ldl:,,,'.'''.....   ...
             .;;'.

""")
# http://pawlovearts.tumblr.com/post/167978580015/fallout-ham
# https://www.ascii-art-generator.org/

_hamster_artwork_08 = (
    '''
           /\\.-="=-./\\
           \\` _':'_ `/
            | o\\ /o |
           =\\       /=
            /'._Y_.'\\
           /   `"`   \\
          /;         ;\\
         | \\         / |
         \\  | /   \\ |  /
         /  | |'-'| |  \\
   jgs  (,,/\\ /   \\ /\\,,)
            `"`   `"`
''')
# http:www.oocities.org/spunk1111/pets2.htm
# http://www.chris.com/ascii/joan/www.geocities.com/SoHo/7373/97oct.html

_hamster_artwork_09 = (
    '''
                c._
      ."````"-"C  o'-.
    _/   \       _..'
   '-\  _/--.<<-'
      `\)     \)  jgs

''')
# http:www.oocities.org/spunk1111/pets2.htm

_hamster_artwork_10 = (
    """
                                         ....''''...
                                   ..,'''';c:'..,:lc,.'..
                                .,:c;'.....   ....':..'::,'.
                             .':c;'.....  .....   .c,...  .','.
                           .,cc;',''.......    ...':.    ....'.'.
                         .:cc;'.''..'::,'..''..   .:,.....     .''.
                      .':o;.         ,.   ..'......:,        ....',.
                    ',,;c'           ,.        .,'.:.   ......     .'
                  ','';:.            ,.          .'c,...           .,;.
                .;;'.:l'             ,.           .c:.       .. ......;.
               ':,...;,              ,.           .;'.'..             .;.
              ';.   ,:.              ,.           .;. ',.          ....:;
             .;. ..;l'               '.           .;.  .,..            .'.
            .:;....;:.               '.           .:.   ',              .'
            ':.    ,;                '.           .:.   ..         .....';.
            ,'     ;,                '.           .:.    .,..  .         ,'
           .;'....,l,                ,.         ..'l,    .'              ,,
           .:,.....:;'''...',.      'lc;;;,;;,;;;;cdo,   .;.   ... ......:,
           .;.     ,lllc;'':l:'...',cdo:,..      .:l,,;. .;.             ,,
            ,'     'ccoo;'.......,;;,:;''.......;;;c' .:.''              ,'
            ':.....;c'.:lc;'......,;,;'.',,;;:ooc',l;...;c;.          ..':.
            .;'     ;;  'ldoc:;,,;;;;,,,,'.',cll:',l;...'::.            ',
             .;.    .:'  .,ldolcc:;,,,,,,'.,c:;::,;l;...'';:'          .,.
              .:'..  'c.   ,odol:;,,,'''..:l;,;:c::o:...''.';;.     ...;,
               .:'....:c..',cddc,'''.,,,,::,,::::;:oc;,,'... ';.      .,.
                .;'    ,c;. ,ol:'...',:ll:'.,:;,;;:ol:::,,'.  ':'....',.
                  ';,..':c'..:;'',;;;clc:;:;;;;;:;coc:ccc:'... .;;..;:.
                    ,cc'.'lc'.,l;';ldoollcccccccc:lolcc:,'..ld, .':;'.
                   .,'''''';:'.co',;,cc;;;;;;cloo:coc::.    .;,..;cc'
                  ',.    .'',coddl:..c:..'',:ldd, .c;.,,.. .   .'. .,,.
                .,'         ..:odooc:::;;;'..;c:,';l;..';'..,;'.     ';.
              .',.       .....;:,,cllc;,,,:::;,;;;coc,,;;,,''..       .;'
         ....,:,.....',,,,;;:ll::cccloooollllolcclodlc::;'...  ...      ,,.
          ...;;,,,,;;;;;:::lolcccccccccc:::;:::,,',,'............        ..
            ............';c;'....'.........   ..... ....  ..
               .........,:'.... ......   ....   ...
                      .:;. ......
                     .:;....
                     ...

""")
# https://www.alisoncoughlan.com/blog/finding-meaning-on-the-hamster-wheel
# https://www.ascii-art-generator.org/

_hamster_artwork_11 = (
    """
                         ...'''''''''....
                    .'';:lllcc::::::clllc:,'..
                 .,;cl:,,,;;;;,,,,,,;;;,',;cl:,'.
               .;cc;,,,,''''.',,,,;;;:;.   .';:c:,.
             .;cc:,,,,'.     .'''''''''''''.  .,:c:,.
            ':c:,';,.                    .','.  .;:::'
           ,cc:',;.                         .     'c:c,
          ,cc:';,                      .           .::c'
         .cc:';,                    .,:;:::'.       .cc:.
        .;cc'.,.           ...'',,,,cl;.':ll;.       ;cc;
        'cc:.          .',;;::;;;;;,;;,'.',;;;;,'.   .:c:.
        ,cc;        .';::;'''''''.'''.''.'',c:';ll,. .:cc'
        ,cc,       '::,''''''''''''.''.'''.,::..cdo,  ;c:,
        ,:c;     .;c,''''''''''''.''''''.''....,;ll.  ;::,
        ':::.    ;c''''''''''''''''''''''''....;od;  .:::,
        .:::'   .c;...'''''''''''''''''.'''....;:,.  .:::.
         ':::.  .,c;..'.'''''''''.......'''',:ll'   .;::;
          ,c::.   .:;.'''.''''...........,,'.',:l;  ;:::.
           ,cc:.   .:c;''.'.;;........',,,,,,;;;,..;:::.
            ':cc,. .cc;'..';ll,,,,,,,,'..       .':::;.
             .;cc:,,;;;;;;;,.......          ..,:cc;.
               .,:cc;;;,..              ..',,;cc;,.
                 .:l:llc;,,,'''''''''',,;clc:,,.
                 .:;::'',,;:cccccccc::;,'''..
                .:;;;      ..........
               .;;;;.
               ;,.;;''........''.''''''''''''''''''.,'
              .c;,,,,,,,',,,,,,,,,,,,,,,,''''',,,,,';,.
                ...................................

""")
# https://www.123rf.com/photo_74430654_stock-vector-cute-cartoon-hamster-running-in-hamster-wheel-vector-pet-illustration-.html
# https://www.ascii-art-generator.org/

# ***

# (lb): I'm never one to be crude, but these are all too funny.
#   For an easter egg within an easter egg, take that!
middle_fingie_01 = (
    '''
...........................
....................../´¯/)
....................,/¯../
.................../..../
............./´¯/'...'/´¯¯`·¸
........../'/.../..../......./¨¯\\
........('(...´...´.... ¯~/'...')
.........\\.................'...../
..........''...\\.......... _.·´
............\\..............(
..............\\.............\\...
...................................
'''.strip()
)
# (lb): Hahahaha! It's got its own domain!
#     https://www.ascii-middle-finger.com/
#
#                    ( ° ͜ʖ͡°)╭∩╮
#
#        (凸 ͡° ͜ʖ ͡°)凸
#                           ╭∩╮(▀̿Ĺ̯▀̿ ̿)ᕗ
#   ╭∩╮(Ο_Ο)╭∩╮

middle_fingie_02_copy_of_01_with_ellipses = (
    '''
   …………………. /´¯/)
   ……………….,/¯../
   ………………./…./
   ………… ./´¯/’…’/´¯¯`·¸
   ……… ./’/…/…./……./¨¯\\
   ……..(‘(…´…´…. ¯~/’…’)
   …… …\\……………..’…../
   ……….…\\………. _.·´
   ……………\\………..(
   …………..\\………….\\…
        '''
)
# "Copy/Paste This Middle Finger"
# https://7tattoo.wordpress.com/2010/03/26/copypaste-this-middle-finger/
# (lb): Hahaha, if you replace the ellipses with periods, you'll see it's
# the same image as before!
#
#   ....................../´¯/)
#   ....................,/¯../
#   .................../..../
#   ............./´¯/’...’/´¯¯`·¸
#   ........../’/.../..../......./¨¯\\
#   ........(‘(...´...´.... ¯~/’...’)
#   .........\\.................’...../
#   ..........”...\\.......... _.·´
#   ............\\..............(
#   ..............\\.............\\...

middle_fingie_03 = (
    '''
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
░░░░░░░░░░░░░░░░░░░░░░░░░░████░░░
░░░░░░░░░░░░░░░░░░░░░░░░░█▀──▀█░░
░░░░░░░░░░░░░░░░░░░░░░░░░█────█░░
░░░░░░░░░░░░░░░░░░░░░░░░░█────█░░
░░░░░░░░░░░░░░░░░░░░░░░░░█────█░░
░░░░░░░░░░░░░░░░░░░░░░░░░█────█░░
░░░░░░░░░░░░░░░░░░░░░░░░░█────█░░
░░░░░░░░░░░░░░░░░░░░░░░░░█────█░░
░░░░░░░░░░░░░░░░░░░░░░░░░█────█░░
░░░░░░░░░░░░░░░░░░░░░░░░░█────█░░
░░░░░░░░░░░░░░░░░░░░░░░░░█────█░░
░░░░░░░░░░░░░░░░░░████░░███████░░
░░░░░░░░░░░░░░░░░██──████▀────█░░
░░░░░░░░░░░░░░░░██────██──────█░░
░░░░░░░░░░░░░░░██────██───────█░░
░░░████████░░░██────██────────█░░
░░█████████████─────██──▄█▄───█░░
░░██████████────────██▄████───█░░
░░█████████──────────▀▀███▀───█░░
░░█████████───────────────────█░░
░░█████████───────────────────█░░
░░█████████───────────────────█░░
░░█████████───────────────────█░░
░░█████████───────────────────█░░
░░█████████──────────────────██░░
░░██████████───────────────███░░░
░░██████████████████████████░░░░░
░░░████████░░░░░░░░░░░░░░░░░░░░░░
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
'''.strip()
)
# https://textart4u.blogspot.com/2013/03/ascii-middle-finger.html

middle_fingie_04 = (
    '''
───────────────────────────────
─────────────▄████▄────────────
────────────▄██████▄───────────
────────────█──────█───────────
────────────█──────█───────────
────────────█─▄▄▄▄─█───────────
────────────█──────█───────────
────────────█──────█───────────
────────────█─▄▄▄▄─█───────────
────────────█──────█───────────
────────────█──────█───────────
────────────█─▄▄▄▄─█───────────
────────────█──────█───────────
────────────█──────█───────────
────────────█─▄▄▄▄─█▄▄▄▄───────
─────▄███████──────█▀█─▀██▄────
─▄█████─────█──────█──█─▀██▄───
─█────█─────█──────█───█──██▄──
─█────█─────█──────█────█──██▄─
─█────█─────█──────█─────█──██─
─█────█─────█──────█─────█─██▀─
─█────█─────█──────█─────███▀──
─█────█─────█──────█─────██▀───
─█───────────────────────██────
─███▄────────────────────█▀────
──▀███▄────────────────▄██─────
────▀████████████████████▀─────
──────▀████████████████▀───────
─────────▀███████████▀─────────
───────────────────────────────
'''.strip()
)
# https://textart4u.blogspot.com/2013/03/ascii-middle-finger.html

middle_fingie_05 = (
    '''
████████████████████████████████████████
██████████████████──▒░██████████████████
█████████████████──────█████████████████
██████████████████▒────█████████████████
██████████████████▒────▒████████████████
██████████████████┬───┬▒████████████████
████████████████▓█┬───░▒████████████████
█████████████████▓▒▓▒─▒▒████████████████
████████████████▓▓█┬─▒▓▓████████████████
████████████████▓─▓▓▓▓▓█████████████████
█████████████████─────▓█████████████████
█████████████████▓▓▓▒░▒█████████████████
█████████████████─▒▓█▓░█████████████████
█████████████████──░▒──█████████████████
█████████████████──────█████████████████
█████████████████─────░█████████████████
█████████████████▒┬──░▒█████████████████
█████████████████────┬▒█████████████████
█████████████████─────██████████████████
████████████████░─────██████████████████
████████████████─────▒▓█████████████████
█████████▓▓▓▒███─────▒▒█████████████████
█████████▒────▒▓▒▒▓▒─▒░█████████████████
████████───▒███▓▒▓▒▓▒░░█████████████████
████████──██▒▒██░░██──▒█▓─▓█████████████
████████─█▓░▓▒─█░──░─▒██─▒▓█████████████
███████──█────░█─────▓██────████████████
██████▓▒██▒───▓█─────▒██────▒██░████████
██████▓▒▓▓▒───▓█─────▒█▓───▓▒█──┬███████
███████─██▒───░█─────░█▓───▓▓█▒──███████
█████░▓─██▓▒──▒█┬────░█▒───███░─┬▓██████
███████─▓▓▓▓▒─┬█░────▒█░───▓██──▓─▓█████
██████▒─▓█▓░▒──█▒█▒──▒█────▒██▒─▓▓▒█████
██████▓▒█▓░▒───█▒┬▓──██────███──▒███████
███████─█┬─▓───█▒──░▒▓█────▒██──▒▓▓█████
███████─█─▓▒──▒█─────▒█─────█▓──▓███████
████████▒─▓───██──────█▒───▒█───▒─██████
████████──┬──┬█───────▓▓────█░────▓█████
████████─────░▒────────▒────▒▓────▓█████
████████─────────────────────┬───▒▓▓████
████████─────────────────────────█─▒████
████████───────────────────────────█████
█████████──▒▒▒▒──────────▒░───▒▓──██████
█████████▓─▒█▓▒─────░▒──█▓▓──▓▓▓▒███████
██████████████▓──▒▓▒█▓──████████████████
████████████████▒▓▓░████████████████████
████████████████████████████████████████
'''.strip()
)
# https://textart4u.blogspot.com/2013/03/ascii-middle-finger.html

# ***

_hamster_corpse_01 = (
    """
                                        .
                                  ..:oodxoooolooc,.
                              .,oxddkxoccc:c::lodkkxl'
                            ,kK0koclloddddoddoll:,:oOOo;
                          .dKkl:;:looll:::::ccdO0d;,,:kKd.
                         .o0k:,,;:;,;;;;;;;;;,,:okxc;;cdx;
                        ;kOo;;;;;;;;;;;;;;;;;,;;,;dOo;,;oc.
                       .o0x:RRRRR:;;;;III:;;;PPPPP:dkc,,c:.
                       :OOclRRccRd;;;;lIo;;;:PP;:PPckd;,:dc.
                       cko;cRRRRRo;;;,lIl,;;:PPPPPc;xKo,;dx'
                       :xl,cRRlRR:;;;,lIo,;;:PPl::;,lKO;,l0o.
                       l0l,:RR;:RRc:::III:;;:PP:;;;;:OKl,lKO.
                       l0o;;:;;;coddoollllloooc;;;;;;xKo,:00'
                      .xKo;;,;coooc;;,,;;;;;cdkxl:;;;lOo,:0X;
                      .ONd,;clcclolc;;;;;;;:locodoc;,cOk;cKX;
                      '0Xo;ldc;;:coxxl:;;lddo:;:cclo:;xk:cKX:
                      .OXl:dl;;;;;;cokkodxdl;;;;::,lo;dOcc0K,
                      .OXolxl;;;;;;;;ldcldc:;;;;;:',dco0o:0K;
                      .kNooOl,;;;;;;cdc;coollc:;;c;'lclOoc0X:
                      .oXd:xOl;;:::oOxll::ccdkkdccc:l:cxc,kNc
                      .dXd;;dOl:c:col:lo;',;:coO0dodc,o0l,oKx;:.
                       lXd,,;lxxd;.;lc,.    .,'ckxoc;;dOc'oOo;ld,
                    ..'l0d,,;;:okko;,;'     .,ckkl;;::xd;lo,..'od;.
                   .;,.':dl,,,;;;coooocc;'':old0o;loooxoll'..'',;c;
                  .''....:kxol:;;;;;cxkxoc::cdkOlco,..,;,...'''''';c'
                .;:'.....,clldxc:oodl;ccclclc;;cldxl,.'''''''''''..co.
               ;:'........''..:;'..;d:''..,dd'.'';;c;''''''''''''.'ll.
              ,o'..',;''''''''''''.'lo'....;dc'''''''''''''''...'.:x:
              .;,,ldo:,'''''.'''''',c:'....',,''''''''''''',;;;;;:cc.
                  ,:'...,;;'...''''''.,:;'.';:,;;'''',,',,.. .'',,.
                  'c:;::;lo;..',''',;,'..''',..'::;;;cc''.
                   .''.   ,olloo;'.',.           ';;;,.
                           'co::cc'


""")
# https://www.ascii-art-generator.org/

# (lb): The rest are derivative works of photos I found after searching:
#   dead hamster, hamster grave, dead guinea pig, hamster corpse.
_hamster_corpse_02 = (
    """
       ...,c,..
     .',:oxo:ld,    ...
     ';;oO0d:okl;ccclol:;''..'...
    .';;;::;;;:;cxOOO00OOOOkxxo;.
    .';;;;;;;;;;;:oxkkOOOOOOkkxl;'.
     ';;;;;;;;;;;;;::ccccccc:::;;;'.
     .,;;;;;;;;;;;;;;;;;;;;;;;;;;;,...
      .,;;;;;;;;;;;;;;;;;;;;;;;;;,. .'.
       .';;;;;;;;;;;;;;;;;;;,,'''.  .'.
         .',,,,',,,,,,,,'....        ....
            .       ..

""")

_hamster_corpse_03 = (
    """
                   ....:d:.
                 .',;;:odc;:l,
               .';;;lk0Oo;:kNd.. ....''..         ..
               .;;;cxKK0o;:d0o;:ldoccddoc:;'....','...
               ';;;;::::;;;::;;ckOOkOOO000OOkOkdodl,.
               ';;;;;;;;;;;;;;;;lxOO0OO00OOOOOOOO0Okl,..
               ';;;;;;;;;;;;;;;;;:ldxkkOOOOOOOkkxxdl:;;'.
               .;;;;;;;;;;;;;;;;;;;;:::cccccccc:::;;;;;,.
               .,;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,'..
                .;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;'..,'.
                .';;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,.  .,.
                  .,;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;'.   .,.
                    .,;;;;;;;;;;;;;;;;;;;;;;;,,'......     .,'..
                      .',,,,''''',,,,,,,'''..               ...'..

""")

_hamster_corpse_04 = (
    """
                           .....
                         ....''...
                     ..'.'..;:,''...................
                   .;:c;;,...';;.......       ................
                 .';:clc;.   .....            ..        ........
              ...........   .          ...    ..   ..         ....
             ...        ..              .                    ...''.
            ...         ..          ..                        ...,.
             .'.                      ..           ..         ...''
              .......      .  ..   .  ..           '.  ..     .'.'.
                 .............,.     ...  .....    ..  ..     .,'..
                        .. ..,;.    .'..... .       .. ..    .,'.
                             .''   .................';,..    .:.
                          ..'.'.  ...            .. .''.'....''.
                          .';,,. ...                 .'.. .'..
                            .'.....               .''''. .'.
                                                  ..'''....
                                                     ..  ..


""")

_hamster_corpse_05_ORIG = (
    """
                          .;;..  ........ .....
                         .:kkdc;''.....    ....',,'.
                        .:looddl:;;,,'.    ..';cloddl'
                         :xkOOxdllc;'.      ..,:codddl'
                         .ck00Okdolc,.      .;:coxkOxc.
                        .':oxdddddOk;.      .dOl:odxo;.
                       ..;clc:;;:cl:....    .':,..',;,.
                       .';;'................        ...
                      .'','..................         ..
                      .'','..........',,'''..
                     ..',,'..........';:::;'... ...
                      .',,,''.........',:;'............
                      .',,;;;,,''......',,.............
                      .',;;;:::::;;,''',,,''''',,,,'...
                      .',,;::ccllllc::;;;;;;;;:cc:;,'..
                      ..';;::cllodddddolccclodkkdl:,...
                      ..';;:cllloddxkO00OkO0XXKOdl:,'.
                         .....'',;;::cllolllocc:;;'..

""")
_hamster_corpse_05 = (
    """
                           .;;..  ........ .....
                          .:kkdc;''.....    ....',,'.
                         .:looddl:;;,,'.    ..';cloddl'
                          :xkOOxdllc;'.      ..,:codddl'
                          .ck00Okdolc,.      .;:coxkOxc.
                         .':oxdddddOk;.      .dOl:odxo;.
                        ..;clc:;;:cl:....    .':,..',;,.
                        .';;'................        ...
                       .'','..................         ..
                       .'','.....{}{} ❌ {}..',,'''..  {}{} ❌ {}
                      ..',,'..........';:::;'... ...
                       .',,,''.........',:;'............
                       .',,;;;,,''......',,.............
                       .',;;;:::::;;,''',,,''''',,,,'...
                       .',,;::ccllllc::;;;;;;;;:cc:;,'..
                       ..';;::cllodddddolccclodkkdl:,...
                       ..';;:cllloddxkO00OkO0XXKOdl:,'.
                          .....'',;;::cllolllocc:;;'..

""".format(
        bg('grey_30'), fg('red'), attr('reset'),
        bg('grey_30'), fg('red'), attr('reset'),
    ))

_hamster_corpse_06 = (
    """
                ''....... ...
               ;ddl;,''.  ..,::;.
               :xOxlc:'.   .;ldxc.
               ,dxddxo'    ;olox:.
              .;:,',;,.... .......
             .',...........      .
             .,''......,;,....
             .,,,'......,,........
             .,;;::;;,'',,''',,'..
             .';:clloolc:::ldo:,.
              .',;:looxxxxxOko:'.
                  .....''''....

""")

_hamster_corpse_07_ORIG = (
    """
            .,c,.',cdc',,;cl:...,.
  ..'.    ';::lc::,:c::;;;ol;:co:...
.,;;:c,..::,,,::;;;;;;;;,;::,;ll;;ldc.
:c;;;:loc;,;;;;;;;;;:;;;;;;;;,,;:cc::l;..
l::',:col;;;;;;;;;;;;;;;;;;;;;:cl:;:;ldoo;.
l::..;:ll;;;;;;;;;;;;;;;;;;;;:cc:..:cllcc;.
l:c'.;:ll:;;;;;;;;;;;;;;;;;;:cl:..,:coc;:ll:
ccc;.;cll;;;;;;;;;;;;;;;;;;;clc,.;:clc;;clc,
.cc:::cl:;;;;;;;;;;;;;;;;;;:ccc:;:ll:;;;:lo:
.clcc:::;;;;;;;;;;;;;;;;;;;:cccc:lc:;;;;:lo:
'l:::;;;;;;;;;;;;;;;::::;;;;;:;;::;;;;;;:l,.
,l;;;;;;;;;;;;;;;:::::::;::;;;;;;;;;;;;;cc.
,l:;;;;;;;:ll:;;;:::::::ooc;;;;;;;;;;;;;l;
.l:;;;;;;;ckOc;;:::::::ckOl;;;;;;;;;;;;:c.
.:c;;;;;;;:lc:;::::::::::c:;;;;;;;;;;;:l,
 'c:;;;;;;;;;;;collllcc:;;;;;;;;;;;;;;c:
  ,l:;;;;;;;;;;:cllcc:;;;;;;;;;;;;;;;;c;
   'cc;;;;;;;;;;;cc;;;:;;;;;;;;;;;;::;:c;.
    .cc;;;;;;;;;;::;;;:;;;;;;;;;;;ldl::oo'
    .c:;;;;;;,,,,;;;;;;;,,,,;;;;;;ldl:c;.
  .;l:;;;;;:l;,;;;;;;;;;;;,:l:;;;;:ll:.
   .ccc:;;:o:  ............'oo:::lc:'.
     'dxllol.               'clccl,

""")
_hamster_corpse_07 = (
    """
                                .,c,.',cdc',,;cl:...,.
                      ..'.    ';::lc::,:c::;;;ol;:co:...
                    .,;;:c,..::,,,::;;;;;;;;,;::,;ll;;ldc.
                    :c;;;:loc;,;;;;;;;;;:;;;;;;;;,,;:cc::l;..
                    l::',:col;;;;;;;;;;;;;;;;;;;;;:cl:;:;ldoo;.
                    l::..;:ll;;;;;;;;;;;;;;;;;;;;:cc:..:cllcc;.
                    l:c'.;:ll:;;;;;;;;;;;;;;;;;;:cl:..,:coc;:ll:
                    ccc;.;cll;;;;;;;;;;;;;;;;;;;clc,.;:clc;;clc,
                    .cc:::cl:;;;;;;;;;;;;;;;;;;:ccc:;:ll:;;;:lo:
                    .clcc:::;;;;;;;;;;;;;;;;;;;:cccc:lc:;;;;:lo:
                    'l:::;;;;;;;;;;;;;;;::::;;;;;:;;::;;;;;;:l,.
                    ,l;;;;;;;;;;;;;;;:::::::;::;;;;;;;;;;;;;cc.
                    ,l:;;;;;;;:\;/;;;:::::::\;/;;;;;;;;;;;;;l;
                    .l:;;;;;;;;;X;;;::::::::;X;;;;;;;;;;;;;:c.
                    .:c;;;;;;;:/;\;:::::::::/;\;;;;;;;;;;;:l,
                     'c:;;;;;;;;;;;collllcc:;;;;;;;;;;;;;;c:
                      ,l:;;;;;;;;;;:cllcc:;;;;;;;;;;;;;;;;c;
                       'cc;;;;;;;;;;;cc;;;:;;;;;;;;;;;;::;:c;.
                        .cc;;;;;;;;;;::;;;:;;;;;;;;;;;ldl::oo'
                        .c:;;;;;;,,,,;;;;;;;,,,,;;;;;;ldl:c;.
                      .;l:;;;;;:l;,;;;;;;;;;;;,:l:;;;;:ll:.
                       .ccc:;;:o:  ............'oo:::lc:'.
                         'dxllol.               'clccl,


""")

_hamster_corpse_08 = (
    """
                   'l'   .:okc.  .,:ldOc
                .,:od'.,:cldo;,;:cccll;...';c'
     ..       .;cc;ldcc:;,;oocc:,,,lxl;:cldd:.
  .;::cc,   .;l:,'':o:,,,,,;,,,;,,,clc;,;oxc,;;:l'
.;l;..,:o:.,l:,',,,,,;;;;;;;;;;;;;;;;;,,;llcccldxc;.
:o;;:::;:dxl;,,;;;;;;;;;;;;;;;;;;;;;;;;,,,,:clc;,,cd:'..
o::l;.:c;lxl;;;;;;;;;;;;;;;;;;;;;;;;;;;;,;clcc:::;:ddlloc.
d;cc' .c::do:;;;;;;;;;;;;;;;;;;;;;;;;;;;;clcc;.'c:cdlcdo;.
d;cl'..;c;oo:;;;;;;;;;;;;;;;;;;;;;;;;;;;clcc'..;c;ldc;:cc:'
o::l;..;c;oo:;;;;;;;;;;;;;;;;;;;;;;;;;;clcc,..'c:cdl:;:::ldl
ll;cc..;c:oo:;;;;;;;;;;;;;;;;;;;;;;;;;:lcc:..,c::oo:;;:ldo;'
'oc:l;.:c:ol;;;;;;;;;;;;;;;;;;;;;;;;;;clcl;.,c:col:;;;;;:cc'
 ,dc:ccc:cl:;;;;;;;;;;;;;;;;;;;;;;;;;;cl:lc:::loc;;;;;;:odl:
 ,doc:::;::;;;;;;;;;;;;;;;;;;;;;;;;;:;cl:cl:col:;;;;;;;;coo,
 co;cc:;;;;;;;;;;;;;;;;;;;;::::;;;;;;;::;;;;cc;;;;;;;;;:oc,,
.ol;;;;;;;;;;;;;;;;;;;;;;;;:::::;;;:;;;;;;;;;;;;;;;;;;;co.
.ol;;;;;;;;;;;;;;;;;;;::::::::::::::;;;;;;;;;;;;;;;;;;;ll.
.ll;;;;;;;;;;;:cc:;;;;;::::::::::loc:;;;;;;;;;;;;;;;;;;o:
.lo;;;;;;;;;;;:oOx:;;;::::::cc::o00o:;;;;;;;;;;;;;;;;;co'
 ;o:;;;;;;;;;;:xKkc;;;::::::::::ckOo:;;;;;;;;;;;;;;;;:o:
 .oc;;;;;;;;;;:cc:;;;:::::::::;;;:::;;;;;;;;;;;;;;;;;lc.
  :o:;;;;;;;;;;;;;;;:lollccccloc:;;;;;;;;;;;;;;;;;;;cl.
  .co;;;;;;;;;;;;;;;;:loooolcc::;;;;;;;;;;;;;;;;;;;;oc
   .ll;;;;;;;;;;;;;;;;;:clc:;;;;;;;;;;;;;;;;;;;;;;;;ll.
    .co:;;;;;;;;;;;;;;;:ll:;;;;;;;;;;;;;;;;;;;;;::;;:o:..
      ;ll:;;;;;;;;;;;;;:c:;;;;:;;;;;;;;;;;;;;::col:;;cxd'
       ;d:;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;lkko::loo,
      'lc;;;;;;;;;,'',,,;;;;;;;;,,,,,;;;;;;;;;:odc:co;
   .;cc:,;;;;;;;coc::;;,,,'''''',,,;;cl:;;;;;;;clllc.
    'ldc,;;;;;;:dl..'',,,,,,,,,,,,,''lxl:;;;::cldl,.
     .::coc;;:cdd.                   .cdolcccdd;..
        :Oxooddo'                     .;cllccc;.

""")

_hamster_corpse_09 = (
    """
              .   .'.                                   .',,'''..
              ....;:'                                  .:::::clodl:'.
               .:lc'      ..                     .    .,;,;;:::coddddc'
                ':,.   .',:c'                  .;oc'. .cc:::::;,lOxldkkl.
                .';.   .,col.                   ':ccc'.;doc;;::;:ooodxxxo'
               ..;:.  .,loo,                     .:oddlcooc;;;;;cldddxkddl.
              .,okd:'',cod:. .....',;;;,'.........,codddooc::::coxxxxkxokd.
              .lkd:::cx00Okc,,;;;;::ccloddxxkO0Ol.':lodxoolccloodOkdxkxdko.
             .,,.:llccodxxdc;;;;;;;;:cccodkkkOKO; .;ol:odoolcldddkOkxOOOOc
            .c:' 'dlcccccodl::;;:ccclodoodxkkO0k;..,llldddlcllllodkOOkkOx'
            .coclxOxxdol::lc:;,,:cloxxc'':dOkOKk;..'coloxxddool:coxkxkOOc.
           ...,clcc:ccdxlcol:;;;:cldkd,  .ckkOKx,  .,l::lxkOkko,',ckOO0o.
          ... .....  .'ddcloolllclodxkc.. 'lx0Kk;.  'dc',lkOOOd'. ,x0Od.
          ..'',ccc:;,,cddlooxkkxdoooxOk:. .'lOXO:.  ,l'  .oOO0o'. 'xOl.
           .,okkOK0OxdddddlcokkOkxxdxkOd.   .oKO;...,l;...:kOo;'. 'xl.
          .''.'',:;.....'coccldkkkkxdxOO,    ,kOc...;c;'. ,xl''...,,.
          ':..  .......';odlc:lodxxxxxO0c.   .:c;.  .;,.. .c:...
           ..',',lxxxxxxOOxoc:clldxxxkO0l'.   .''.   ...   .....
             'l:;:clolollccoxddxxkkOOKKd;'..  .....    ..    ..
              ';'  .........ckOOOO000Oo'........','.  .... ...
               'l:,',cc,,,;cxO0Oxdl;'.         ...        ..
                .,:::clloooolcc,.
                             ..
          ...                ..
          ...

""")

_hamster_corpse_10 = (
    """
                     .;ccccc:,
                   ,oocccldxd;.
                  .okollolc;.
                   .''.....','.
                      ';llcc:okoc;.
                   .,,;lc;;;:cdOOk,
                .;lolcoxxdoolllkKx.
               .oxlcdKd',::lddxkxd,
               'c...',.     .;loloo.
               .;.      .... .;clldc..
                .;,. .''''''':olclol,','
                 .;l:,.      .ldoc.    ,;.
              .c,.'....  ;o;.;dddx,.. ..':.
               ,:,'':o;,okOxoxxddxdoo;;o:,;:;.
               'c,..'lxxdolllllloodl..'co;','
             .,:.  .colllccclccllldl.  .;'
             ,l.   ,dolccclllllllldc.   ;;
             ,c    .ldollcccllccloo,    ,,
             ':.    ;ddoolcllcllol'     ;'
             .;'     'codoollooo;.     ,;
              ..     ..';clc:::'. ..  ',.
                        ....           ...

""")
# 2018-05-17 17:55: (lb) I generated this a few hours ago and now
# I cannot recall what the source image was.

# ***

_infection_notice = (
    """
╔═════════════════════════════════════════════════════════════════════════════════╗
║ ╭─────────────────────────────────────────────────────────────────────────────╮ ║
║ │                                                                             │ ║
║ │  ▌ ▌         ▌            ▐         ▌           ▌            ▐              │ ║
║ │  ▝▞▞▀▖▌ ▌▙▀▖ ▛▀▖▝▀▖▛▚▀▖▞▀▘▜▀ ▞▀▖▙▀▖ ▛▀▖▝▀▖▞▀▘ ▞▀▌▌ ▌▞▀▘▞▀▖▛▀▖▜▀ ▞▀▖▙▀▖▌ ▌   │ ║
║ │   ▌▌ ▌▌ ▌▌   ▌ ▌▞▀▌▌▐ ▌▝▀▖▐ ▖▛▀ ▌   ▌ ▌▞▀▌▝▀▖ ▌ ▌▚▄▌▝▀▖▛▀ ▌ ▌▐ ▖▛▀ ▌  ▚▄▌▗▖ │ ║
║ │   ▘▝▀ ▝▀▘▘   ▘ ▘▝▀▘▘▝ ▘▀▀  ▀ ▝▀▘▘   ▘ ▘▝▀▘▀▀  ▝▀▘▗▄▘▀▀ ▝▀▘▘ ▘ ▀ ▝▀▘▘  ▗▄▘▝▘ │ ║
║ │                                                                             │ ║
║ ╰─────────────────────────────────────────────────────────────────────────────╯ ║
╚═════════════════════════════════════════════════════════════════════════════════╝

                            Press SPACE BAR to continue
""")


# ***


def fetch_asciis(posits):
    hamster_art = hamster_artwork()
    try:
        arts = [hamster_art[int(posit)] for posit in posits]
    except IndexError:
        arts = _fetch_fingie()
    return arts


def _fetch_fingie():
    fingies_art = fingies_artwork()
    one_art_please = random.choice(fingies_art)
    if one_art_please == fingies_art[0]:
        one_art_please = _ascii_fill_left(one_art_please)
    arts = [one_art_please]
    return arts


def _ascii_fill_left(one_art_please):
    max_width = 0
    for line in one_art_please.splitlines():
        max_width = max(max_width, len(line))

    term_width, _term_height = click.get_terminal_size()

    # Not sure why we need 2 extra spaces to not wrap.
    # But add more to not crowd right border.
    empty_cols = term_width - len(line) - 9
    if empty_cols <= 0:
        return one_art_please

    repeat_ch = one_art_please[0]
    lpadding = repeat_ch * empty_cols

    new_art = ''
    for line in one_art_please.splitlines():
        # From https://docs.python.org/3/library/os.html
        #  "Do not use os.linesep as a line terminator when writing files
        #   opened in text mode (the default); use a single '\n' instead,
        #   on all platforms."
        new_art += lpadding + line + "\n"

    return new_art


def randomster():
    randodent = random.choice(hamster_artwork())
    centerful = center_lines(randodent)
    return centerful


def lifeless():
    return random.choice(dead_hamsters_society())


def center_lines(lines):
    term_width = click.get_terminal_size()[0]
    line_width = max([len(line) for line in lines.splitlines()])
    avail_width = term_width - line_width
    return justify_line(lines, avail_width)


def justify_line(lines, avail_width):
    if avail_width <= 0:
        return lines
    # Meh. Centered seems too centered, e.g.,
    #   half_left = int(avail_width / 2)
    middleish = int(0.33 * avail_width)
    rand_left = random.choice(range(avail_width))
    padding_l = random.choice([middleish, rand_left])
    justified = "\n".join([' ' * padding_l + line for line in lines.splitlines()])
    return justified


# MEH: (lb): Doesn't really belong in this module...
def curly_quote(obj):
    # FIXME/2018-05-18: (lb): Make config setting for this.
    #    ascii_only = controller.config['term.ascii_only']
    ascii_only = False
    if ascii_only or (os.name == 'nt'):
        return "'{}'".format(obj)
    else:
        # Vim digraph: <Ctrl-l> '6 / <Ctrl-l> '9
        return "‘{}’".format(obj)


# MEH: (lb): Doesn't really belong in this module...
def curly_quotes(obj):
    # FIXME/2018-05-18: (lb): Make config setting for this.
    #    ascii_only = controller.config['term.ascii_only']
    ascii_only = False
    if ascii_only or (os.name == 'nt'):
        return '"{}"'.format(obj)
    else:
        # Vim digraph: <Ctrl-l> "6 / <Ctrl-l> "9
        return '“{}”'.format(obj)

