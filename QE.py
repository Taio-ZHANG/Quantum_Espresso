from pymatgen.core import Structure, Element  

def get_clean_path(input_path):  
    """清除路径字符串两端的引号和多余空格"""  
    return input_path.strip().strip('"').strip("'")  

def add_zeros_to_coordinates(coordinates):  
    print("以下是按z轴坐标从低到高排序的原子坐标：")  
    sorted_coordinates = sorted(coordinates, key=lambda x: x[1][2])  # 按z轴排序  
    for i, (label, coord) in enumerate(sorted_coordinates, start=1):  
        print(f"{i}: {label} {coord[0]:.10f} {coord[1]:.10f} {coord[2]:.10f}")  

    start_line = int(input("请输入要添加 '0 0 0' 的起始行（从1开始计数）：")) - 1  
    end_line = int(input("请输入要添加 '0 0 0' 的结束行（从1开始计数）：")) - 1  
    
    # 确保输入的行数在有效范围内  
    if start_line < 0 or end_line >= len(sorted_coordinates) or start_line > end_line:  
        print("输入的行数范围无效。")  
        return coordinates  

    # 添加 "0 0 0" 到指定行  
    modified_coordinates = []  
    for i, (label, coord) in enumerate(sorted_coordinates):  
        if start_line <= i <= end_line:  
            modified_coord = f"{label} {coord[0]:.10f} {coord[1]:.10f} {coord[2]:.10f} 0 0 0"  
        else:  
            modified_coord = f"{label} {coord[0]:.10f} {coord[1]:.10f} {coord[2]:.10f}"  
        modified_coordinates.append(modified_coord)  

    return modified_coordinates  

def main():  
    # 获取用户输入的CIF文件路径  
    cif_file = input("请输入cif文件的路径: ")  
    cif_file = get_clean_path(cif_file)  
    
    # 读取CIF文件  
    try:  
        structure = Structure.from_file(cif_file)  
    except Exception as e:  
        print(f"读取cif文件失败: {e}")  
        return  
    
    # 提取原子种类和数量  
    species = structure.composition.elements  
    species_list = [str(sp) for sp in species]  

    # 提取晶胞参数  
    lattice = structure.lattice  
    cell_parameters = lattice.matrix  

    # 提取原子坐标  
    atomic_positions = structure.frac_coords  
    atom_labels = [str(site.species_string) for site in structure]  
    
    # 将原子标签和坐标结合为二元组列表  
    coordinates_with_labels = list(zip(atom_labels, atomic_positions))  

    # 将原子坐标和标签结合为字符串列表  
    coordinates_str = [  
        f"{atom_labels[i]} {pos[0]:.10f} {pos[1]:.10f} {pos[2]:.10f}"   
        for i, pos in enumerate(atomic_positions)  
    ]  

    # 调用函数添加 "0 0 0" 到选择的原子坐标  
    modified_coordinates = add_zeros_to_coordinates(coordinates_with_labels) 

    # Quantum ESPRESSO输入文件模板  
    qe_input_template = """&CONTROL  
  title='ZT',   
  calculation='relax',   
  pseudo_dir='./',   
  outdir='./tmp',   
  verbosity='high',  
  forc_conv_thr=1.0d-4,   
  nstep=100,  
/  
&SYSTEM  
  ibrav= 0,   
  nat= {nat},   
  ntyp= {ntyp},   
  occupations = 'smearing',   
  smearing = 'gauss',   
  degauss = 1.0d-2,  
  ecutwfc = 30,   
  ecutrho = 360,  
  vdw_corr = 'DFT-D3',
  dftd3_version = 6 
/  
&ELECTRONS  
  conv_thr = 1.0d-6  
  mixing_beta = 0.5d0  
/
&IONS
/
&CELL
  press_conv_thr=0.1
/  
ATOMIC_SPECIES  
{atomic_species}  
CELL_PARAMETERS (angstrom)  
{cell_parameters}  
ATOMIC_POSITIONS (crystal)  
{atomic_positions}  
K_POINTS {{gamma}} 
"""  

    nat = len(atom_labels)  # 原子总数  
    ntyp = len(species_list)  # 原子种类数  

    # ATOMIC_SPECIES with real atomic masses  
    atomic_species = "\n".join([  
        f"{element} {Element(element).atomic_mass:.3f} {element}.UPF" for element in species_list  
    ])  

    # CELL_PARAMETERS  
    cell_parameters_str = "\n".join(["{:.6f} {:.6f} {:.6f}".format(*row) for row in cell_parameters])  

    # 转换坐标列表为字符串  
    atomic_positions_str = "\n".join(modified_coordinates)  

    # 填充输入模板  
    qe_input_content = qe_input_template.format(  
        nat=nat,  
        ntyp=ntyp,  
        atomic_species=atomic_species,  
        cell_parameters=cell_parameters_str,  
        atomic_positions=atomic_positions_str  
    )  

    # 获取用户输入的输出文件路径  
    output_file = input("请输入要保存的QE输入文件路径: ")  
    output_file = get_clean_path(output_file)  
    try:  
        with open(output_file, "w") as f:  
            f.write(qe_input_content)  
        print(f"Quantum ESPRESSO 输入文件已更新并保存为 '{output_file}'.")  
    except Exception as e:  
        print(f"保存文件失败: {e}")  

if __name__ == "__main__":  
    main()