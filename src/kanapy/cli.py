# -*- coding: utf-8 -*-
import os, sys
import shutil, json
import click

from kanapy.util import ROOT_DIR, MAIN_DIR 
from kanapy.input_output import particleStatGenerator, write_position_weights
from kanapy.input_output import write_abaqus_inp, write_output_stat
from kanapy.input_output import extract_volume_sharedGBarea
from kanapy.packing import packingRoutine
from kanapy.voxelization import voxelizationRoutine
from kanapy.analyze_texture import textureReduction

@click.group()
@click.pass_context
def main(ctx):    
    pass    


@main.command()
@click.pass_context
def install(ctx):    
    """ Install kanapy's geometry packing module."""
    
    click.echo('')
    os.system("conda install -y -c conda-forge --file {0}/requirements.txt".format(MAIN_DIR))   
    os.system("pip install -e {0}".format(MAIN_DIR)) 
    
    # For Kanapy bash auto completion
    os.system("echo '# For KANAPY bash autocompletion' >> ~/.bashrc")
    os.system("echo '. {}' >> ~/.bashrc".format(ROOT_DIR+'/kanapy-complete.sh'))  


@main.command()
@click.pass_context
def unittests(ctx):    
    """ Runs unittests built within kanapy."""
    
    click.echo('')
    os.system("pytest {0}/tests/ -v".format(MAIN_DIR))      
    click.echo('')    
        
    
@main.command()
@click.pass_context
def builddocs(ctx):    
    """ Generates a HTML-based reference documentation."""
    
    click.echo('')
    os.system("make -C {0}/docs/ clean && make -C {0}/docs/ html".format(MAIN_DIR))      
    click.echo('')
    click.echo("The HTML documentation can be found at '/path/to/your/kanapy/docs/index.html'")
    click.echo('')
    
       
@main.command()
@click.option('--filename', default=None, help='Input statistics file name in the current directory.')
@click.pass_context
def statgenerate(ctx, filename: str):    
    """ Generates particle statistics based on the data provided in the input file."""
                
    if filename == None:
        click.echo('')
        click.echo('Please provide the name of the input file available in the current directory', err=True)
        click.echo('For more info. run: kanapy statgenerate --help\n', err=True)
        sys.exit(0)         
    else:
        cwd = os.getcwd()
        if not os.path.exists(cwd + '/{}'.format(filename)):
            click.echo('')
            click.echo("Mentioned file: '{}' does not exist in the current working directory!\n".format(filename), err=True)
            sys.exit(0)        
        particleStatGenerator(cwd + '/' + filename)           

        
@main.command()
@click.pass_context
def pack(ctx):
    """ Packs the particles into a simulation box."""
    packingRoutine()


@main.command()
@click.option('--timestep', help='Time step for voxelization.')
@click.pass_context
def voxelize(ctx, timestep: int):
    """ Generates the RVE by assigning voxels to grains.""" 

    if timestep == None:
        click.echo('')    
        click.echo('Please provide the timestep value for voxelization!', err=True)
        click.echo('For more info. run: kanapy voxelize --help\n', err=True)
        sys.exit(0)         
    voxelizationRoutine(timestep)
    

@main.command()
@click.pass_context
def abaqusoutput(ctx):
    """ Writes out the Abaqus (.inp) file for the generated RVE."""    
    write_abaqus_inp()
    
        
@main.command()
@click.pass_context
def outputstats(ctx):
    """ Writes out the particle- and grain diameter attributes for statistical comparison. Final RVE 
    grain volumes and shared grain boundary surface areas info are written out as well."""
    write_output_stat()
    extract_volume_sharedGBarea()
        
                
@main.command()
@click.option('--timestep', help='Time step for which Neper input files will be generated.')
@click.pass_context
def neperoutput(ctx, timestep: int):
    """ Writes out particle position and weights files required for tessellation in Neper."""

    if timestep == None:
        click.echo('')    
        click.echo('Please provide the timestep value for generating ouput!', err=True)
        click.echo('For more info. run: kanapy neperoutput --help\n', err=True)
        sys.exit(0)                
    write_position_weights(timestep)


@main.command()
@click.pass_context
def setupTexture(ctx):    
    """ Stores the user provided MATLAB & MTEX paths for texture analysis."""
    setPaths()                    


def chkVersion(matlab):
    ''' Read the version of Matlab'''
    output = os.popen('{} -r quit -nojvm | grep "R201[0-9][ab]"'.format(matlab)).read()                
    version = output.split()[0]
    version = int(version[1:-1])
    return version
    
        
def setPaths():
    ''' Requests user input for MATLAB & MTEX installation paths'''
    
    # For MATLAB executable
    print('')
    status1 = input('Is MATLAB installed in this system (yes/no): ')
    
    if status1 == 'yes' or status1 == 'y' or status1 == 'Y' or status1 == 'YES':
        print('Searching your system for MATLAB ...')
        MATLAB = shutil.which("matlab")        

        if MATLAB:
            decision1 = input('Found MATLAB in {0}, continue (yes/no): '.format(MATLAB))
            
            if decision1 == 'yes' or decision1 == 'y' or decision1 == 'Y' or decision1 == 'YES':                

                version = chkVersion(MATLAB)        # Get the MATLAB version
                if version < 2015:
                    click.echo('')
                    click.echo('Sorry!, Kanapy is compatible with MATLAB versions 2015a and above\n', err=True)
                    sys.exit(0)
                else:
                    userpath1 = MATLAB

            elif decision1 == 'no' or decision1 == 'n' or decision1 == 'N' or decision1 == 'NO':
                userinput = input('Please provide the path to MATLAB executable: ')
                
                version = chkVersion(userinput)
                if version < 2015:
                    click.echo('')
                    click.echo('Sorry!, Kanapy is compatible with MATLAB versions 2015a and above\n', err=True)
                    sys.exit(0)
                else:
                    userpath1 = userinput
                                    
            else:
                click.echo('Invalid entry!, Run: kanapy setuptexture again', err=True)
                sys.exit(0) 
                            
        elif not MATLAB:
            print('No MATLAB executable found!')            
            userinput = input('Please provide the path to MATLAB executable: ')
            
            version = chkVersion(userinput)
            if version < 2015:
                click.echo('')
                click.echo('Sorry!, Kanapy is compatible with MATLAB versions 2015a and above\n', err=True)
                sys.exit(0)
            else:
                userpath1 = userinput
                    
                    
        # For MTEX installation path
        print('')
        status2 = input('Is MTEX installed in this system (yes/no): ')

        if status2 == 'yes' or status2 == 'y' or status2 == 'Y' or status2 == 'YES':                    
            userpath2 = input('Please provide the path to MTEX installation: ')                                         
        elif status2 == 'no' or status2 == 'n' or status2 == 'N' or status2 == 'NO':
            print("Kanapy's texture analysis code requires MTEX. Please install it from: https://mtex-toolbox.github.io/download.")
            print('')
            userpath2 = False
        else:
            click.echo('Invalid entry!, Run: kanapy setuptexture again', err=True)
            sys.exit(0)  
        
                     
    elif status1 == 'no' or status1 == 'n' or status1 == 'N' or status1 == 'NO':
        print("Kanapy's texture analysis code requires MATLAB. Please install it.")
        print('')
        userpath1 = False
    else:
        click.echo('Invalid entry!, Run: kanapy setuptexture again', err=True)
        sys.exit(0)        
        
    # Create a file in the 'src/kanapy' folder that stores the paths
    if userpath1 and userpath2:        
        
        pathDict = {'MATLABpath': '{}'.format(userpath1), 'MTEXpath': '{}'.format(userpath2)}                
        path_path = ROOT_DIR+'/PATHS.json'
        
        if os.path.exists(path_path):
            os.remove(path_path)

        with open(path_path,'w') as outfile:
            json.dump(pathDict, outfile, indent=2)                
        
        print('')
        print('Kanapy is now configured for texture analysis!\n')


@main.command()
@click.option('--ebsd', default=None, help='EBSD (.mat) file name located in the current directory.')
@click.option('--grains', default=None, help='Grains (.mat) file name located in the current directory.')
@click.option('--kernel', default=None, help='Optimum kernel shape factor as float (in radians).')
@click.option('--fit_mad', default='no', help='Fit Misorientation Angle Distribution (yes/no).')
@click.pass_context
def reducetexture(ctx, ebsd: str, grains: str, kernel: float, fit_mad: bool):
    """ Texture reduction algorithm with optional Misorientation angle fitting."""
    
    if ebsd==None:
        click.echo('')
        click.echo('Please provide some EBSD inputs for texture reduction!') 
        click.echo('For more info, run: kanapy reducetexture --help\n', err=True)
        sys.exit(0)
    else:
        cwd = os.getcwd()
        arg_dict = {}           
        if ebsd != None:
            if not os.path.exists(cwd + '/{}'.format(ebsd)):
                click.echo('')
                click.echo("Mentioned file: '{}' does not exist in the current working directory!\n".format(ebsd), err=True)
                sys.exit(0)
            else:
                arg_dict['ebsdMatFile'] = cwd + '/{}'.format(ebsd)

        if grains != None:
            if not os.path.exists(cwd + '/{}'.format(grains)):
                click.echo('')
                click.echo("Mentioned file: '{}' does not exist in the current working directory!\n".format(grains), err=True)
                sys.exit(0)
            else:        
                arg_dict['grainsMatFile'] = cwd + '/{}'.format(grains)
                
        if kernel != None:
            arg_dict['kernelShape'] = kernel        
            
        if fit_mad == 'yes' or fit_mad == 'y' or fit_mad == 'Y' or fit_mad == 'YES': 
            arg_dict['MisAngDist'] = fit_mad            
            textureReduction(arg_dict)      
                  
        elif fit_mad == 'no' or fit_mad == 'n' or fit_mad == 'N' or fit_mad == 'NO': 
            textureReduction(arg_dict)
        else:
            click.echo('')
            click.echo('Invalid entry! Run: kanapy reducetexture --help\n', err=True)
            sys.exit(0)
        
    
def start():
    main(obj={})

    
if __name__ == '__main__':
    start()
