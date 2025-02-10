# First create inlist_project with MESA parameters
with open('inlist_project', 'w') as f:
    f.write("""
&star_job
    show_log_description_at_start = .false.
    create_pre_main_sequence_model = .true.
    save_model_when_terminate = .true.
    save_model_filename = 'final.mod'
    pgstar_flag = .false.
/ 

&controls
    initial_mass = {mass}
    initial_z = 0.02
    use_Type2_opacities = .true.
    mixing_length_alpha = 2.0

    initial_y = 0.28
    
    max_age = 1d8
    mesh_delta_coeff = 1.0
    varcontrol_target = 1d-4
    
    ! Output controls
    photo_interval = 50
    profile_interval = 50
    history_interval = 1
    terminal_interval = 10
    write_header_frequency = 10
/
""")

import numpy as np
import matplotlib.pyplot as plt
from subprocess import run
import os

def salpeter_imf(mass_min, mass_max, num_stars):
    """Generate masses following Salpeter IMF: dN/dM ∝ M^(-2.35)"""
    alpha = -2.35
    u = np.random.random(num_stars)
    alpha1 = alpha + 1
    m1 = mass_min**alpha1
    m2 = mass_max**alpha1
    masses = (m1 + (m2 - m1)*u)**(1/alpha1)
    return masses

def run_mesa_models(masses):
    """Run MESA for each mass in the distribution"""
    results = []
    for mass in masses:
        with open('inlist_project', 'r') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines):
            if 'initial_mass' in line:
                lines[i] = f'    initial_mass = {mass}\n'
        
        with open('inlist_project', 'w') as f:
            f.writelines(lines)
        
        run(['./rn'], check=True)
        
        if os.path.exists('LOGS/history.data'):
            results.append({'mass': mass, 'success': True})
        else:
            results.append({'mass': mass, 'success': False})
    
    return results

def analyze_distribution():
    masses = salpeter_imf(0.1, 50, 1000)  # Generate 1000 stars between 0.1 and 50 solar masses
    
    plt.figure(figsize=(10, 6))
    plt.hist(masses, bins=50, density=True, alpha=0.6, label='Generated Distribution')
    
    mass_range = np.linspace(0.1, 50, 1000)
    salpeter = mass_range**(-2.35)
    salpeter /= np.trapz(salpeter, mass_range)  # Normalize
    plt.plot(mass_range, salpeter, 'r-', label='Salpeter IMF')
    
    plt.xlabel('Mass (Solar Masses)')
    plt.ylabel('Normalized Frequency')
    plt.title('Generated Mass Distribution vs Salpeter IMF')
    plt.legend()
    plt.yscale('log')
    plt.xscale('log')
    plt.grid(True)
    plt.savefig('mass_distribution.png')
    plt.close()
    
    print("Running MESA models...")
    results = run_mesa_models(masses)
    
    successful_runs = sum(1 for r in results if r['success'])
    print(f"Successfully ran {successful_runs} out of {len(masses)} models")
    
    return results

if __name__ == "__main__":
    results = analyze_distribution()