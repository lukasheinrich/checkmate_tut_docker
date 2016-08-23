#!/usr/bin/python
import click
import os
import subprocess
import shlex
import json


@click.group()
def cli():
    pass

@cli.command()
@click.argument('template')
@click.argument('stop_mass')
@click.argument('neutralino_mass')
@click.argument('outputSLHA')
def prepare_slha(template,stop_mass,neutralino_mass,outputSLHA):
    with open(template) as f:
        with open(outputSLHA,'w') as filled:
            filled.write(
                f.read().format(
                    __stop_mass__ = stop_mass,
                    __neutralino_mass__   = neutralino_mass,
                )
            )

@cli.command()
@click.option('-e','--events', default = 10000)
@click.option('-s','--seed', default = 123456)
@click.option('-o','--output', default = 'output.hepmc')
@click.option('-r','--runprefix', default = 'herwigrun')
@click.option('-l','--slhafile', default = 'input.slha')
@click.argument('template')
@click.argument('filledfile')
def prepare_runcard(events,seed,output,runprefix,slhafile,template,filledfile):
    with open(template) as f:
        with open(filledfile,'w') as filled:
            filled.write(
                f.read().format(
                    __events__ = events,
                    __seed__   = seed,
                    __output__ = output,
                    __runprefix__ = runprefix,
                    __slhafile__ = slhafile
                )
            )


@cli.command()
@click.argument('stop_mass')
@click.argument('pdf')
@click.argument('xsecjson')
def compute_xsec(stop_mass,pdf,xsecjson):
    olddir = os.path.realpath(os.curdir)
    os.chdir('/home/checkmate/tools/nllfast')
    out,err = subprocess.Popen(shlex.split('./nllfast st {} {}'.format(pdf,stop_mass)), stdout = subprocess.PIPE).communicate()
    os.chdir(olddir)
    lines = out.splitlines()
    fieldnum,label = [(i-1,field) for i,field in enumerate([l for l in lines if 'ms[GeV]' in l][0].split()) if 'NLL+NLO' in field][0]
    unit = label.replace('NLL+NLO','').translate(None,'[]')
    xsec = lines[-1].split()[fieldnum]
    json.dump({'xsec':xsec,'unit':unit},open(xsecjson,'w'))

@cli.command()
@click.option('-n','--name', default = 'checkmate')
@click.option('-s','--seed', default = 123456)
@click.option('-o','--outputdir',default = 'output')
@click.argument('template')
@click.argument('xsecfile')
@click.argument('eventfile')
@click.argument('analysis')
@click.argument('runcard_out')
def prepare_checkmate(name,seed,outputdir,template,xsecfile,eventfile,analysis,runcard_out):
    xsecdata = json.load(open(xsecfile))
    with open(template) as f:
        with open(runcard_out,'w') as filled:
            filled.write(
                f.read().format(
                    __name__ = name,
                    __analysis__ = analysis,
                    __seed__   = seed,
                    __outputdir__ = outputdir,
                    __xsec_value__ = xsecdata['xsec'],
                    __xsec_unit__ = xsecdata['unit'],
                    __inputhepmc__ = eventfile
                )
            )



@cli.command()
@click.argument('checkmateoutput')
@click.argument('limitfile')
def recast_format(checkmateoutput,limitfile):
    min_cls_obs, min_cls_exp = None, None
    sr_data =  open(checkmateoutput).readlines()[2:]
    for sr in sr_data:
        this_lines = sr.split()
        cls_obs, cls_exp = this_lines[8],this_lines[10]
        if (cls_exp < min_cls_exp) or (min_cls_exp is None):
            min_cls_obs, min_cls_exp = cls_obs, cls_exp
    recast_data = {
        'lower_2sig_expected_CLs':None,
        'lower_1sig_expected_CLs':None,
        'expected_CLs':min_cls_exp,
        'upper_1sig_expected_CLs':None,
        'upper_2sig_expected_CLs':None,
        'observed_CLs':min_cls_obs,
        'log_likelihood_at_reference':None
    }
    json.dump(recast_data,open(limitfile,'w'))

if __name__ == '__main__':
    cli()
