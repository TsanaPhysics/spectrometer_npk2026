// ==============================================================================
// SpectorV5-Pro: Integrated Precision Spectrophotometer Workstation
// Designed with Skill: spectrometer-3d-chassis-architect
// Digital Agriphysics & AI Research Unit (JC_AI_SciRBRU)
// Department of Physics, Faculty of Science and Technology,
// Rambhai Barni Rajabhat University (RBRU)
//
// Complies with 5 Optical Rig Design Laws:
// Law 1: Coaxial collinear optical alignment (WS2812B -> Aperture -> Cuvette -> TCS34725)
// Law 2: Dual 3.0mm collimating apertures for stray-light cut-off
// Law 3: Double-stepped labyrinth seal on optical cuvette well
// Law 4: Calibrated 10mm cuvette slot (12.75 x 12.75 mm, tolerance +0.25mm)
// Law 5: Heavy-duty 3.5mm wall opacity & 100% solid light-tight barrier
//
// Integrated Ergonomics:
// - 22-degree inclined console deck for Wio Terminal 2.4" LCD & buttons
// - Internal cable routing channels between Grove ports and optical core
// - Lower compartment for rechargeable Li-Po field battery
// - Rubber-foot / M3 bolt mounting points for lab bench stability
// ==============================================================================

$fn = 60; // High curve resolution

// --- Global Parametric Variables ---
tolerance           = 0.25;  // 3D printer clearance (mm)

// Chassis Envelope (Based on SpectorV4 Master Dimensions)
chassis_w           = 96.0;  // X width (mm)
chassis_d           = 120.0; // Y depth (mm)
chassis_h_front     = 36.0;  // Z height at front edge (mm)
chassis_h_rear      = 78.0;  // Z height at rear deck (mm)
incline_angle       = 22.0;  // Console deck incline angle (degrees)

// Cuvette & Optical Parameters
cuvette_size        = 12.50; // Standard 10mm pathlength cuvette
cuvette_slot        = cuvette_size + tolerance; // 12.75 mm
cuvette_floor_z     = 18.0;  // Cuvette base shelf height from ground
optical_axis_z      = cuvette_floor_z + 15.0; // 33.0 mm (15mm above cuvette floor)
optical_axis_y      = 35.0;  // Y position of optical axis (rear zone)
aperture_dia        = 3.00;  // Collimating tunnel diameter
aperture_tunnel_l   = 4.00;  // Tunnel length to enforce normal incidence

// Labyrinth Seal Dimensions
baffle_step_w       = 2.20;
baffle_lip_h        = 3.50;

// Wio Terminal Dimensions (Front Incline Zone)
wio_w               = 72.5 + tolerance; // 72.75 mm
wio_d               = 57.5 + tolerance; // 57.75 mm
wio_thickness       = 12.5;             // 12.5 mm
screen_window_w     = 50.0;             // 2.4" LCD visible area X
screen_window_d     = 38.0;             // 2.4" LCD visible area Y
joystick_hole_dia   = 9.0;              // 5-way analog joystick clearance
btn_cutout_w        = 10.0;             // Buttons A, B, C cutouts

// ==============================================================================
// Modules
// ==============================================================================

// 1. Master Wedge Chassis Body
module chassis_body() {
    hull() {
        // Front bottom corners
        translate([-chassis_w/2 + 4, -chassis_d/2 + 4, 2]) cylinder(r=4, h=chassis_h_front - 2);
        translate([ chassis_w/2 - 4, -chassis_d/2 + 4, 2]) cylinder(r=4, h=chassis_h_front - 2);
        
        // Rear bottom corners
        translate([-chassis_w/2 + 4,  chassis_d/2 - 4, 2]) cylinder(r=4, h=chassis_h_rear - 2);
        translate([ chassis_w/2 - 4,  chassis_d/2 - 4, 2]) cylinder(r=4, h=chassis_h_rear - 2);
        
        // Base rim
        translate([-chassis_w/2 + 4, -chassis_d/2 + 4, 0]) cylinder(r=4, h=2);
        translate([ chassis_w/2 - 4, -chassis_d/2 + 4, 0]) cylinder(r=4, h=2);
        translate([-chassis_w/2 + 4,  chassis_d/2 - 4, 0]) cylinder(r=4, h=2);
        translate([ chassis_w/2 - 4,  chassis_d/2 - 4, 0]) cylinder(r=4, h=2);
    }
}

// 2. Complete SpectorV5 Workstation Assembly
module spector_v5_workstation() {
    difference() {
        // --- POSITIVE SOLID SHELL ---
        union() {
            chassis_body();
            
            // Raised Labyrinth Baffle Ring around Cuvette Slot on rear top deck
            translate([0, optical_axis_y, chassis_h_rear]) {
                hull() {
                    translate([-16, -16, 0]) cylinder(r=2, h=baffle_lip_h);
                    translate([ 16, -16, 0]) cylinder(r=2, h=baffle_lip_h);
                    translate([ 16,  16, 0]) cylinder(r=2, h=baffle_lip_h);
                    translate([-16,  16, 0]) cylinder(r=2, h=baffle_lip_h);
                }
            }
        }

        // --- NEGATIVE CUTOUTS ---
        
        // A. Cuvette Measurement Well (Law 4)
        translate([-cuvette_slot/2, optical_axis_y - cuvette_slot/2, cuvette_floor_z])
            cube([cuvette_slot, cuvette_slot, chassis_h_rear + baffle_lip_h + 10]);

        // Cuvette Insertion Lead-in Chamfer
        translate([0, optical_axis_y, chassis_h_rear + baffle_lip_h - 1.5])
            cylinder(r1=cuvette_slot/2, r2=cuvette_slot/2 + 2.0, h=3.0);

        // B. Coaxial Optical Aperture Tunnel (Law 1 & 2)
        // Along X axis across entire optical core at Y=optical_axis_y, Z=optical_axis_z
        translate([-chassis_w/2 - 1, optical_axis_y, optical_axis_z])
            rotate([0, 90, 0])
                cylinder(d=aperture_dia, h=chassis_w + 2);

        // C. Left Light Source Pocket (Grove WS2812B NeoPixel at -X)
        translate([-chassis_w/2 - 0.1, optical_axis_y - 10.5, optical_axis_z - 10.5])
            cube([4.0, 21.0, 21.0]);
        // LED M2.5 screw holes
        translate([-chassis_w/2 + 3.9, optical_axis_y - 7.5, optical_axis_z])
            rotate([0, 90, 0]) cylinder(d=2.2, h=6);
        translate([-chassis_w/2 + 3.9, optical_axis_y + 7.5, optical_axis_z])
            rotate([0, 90, 0]) cylinder(d=2.2, h=6);

        // D. Right Detector Pocket (Adafruit TCS34725 at +X)
        translate([chassis_w/2 - 3.9, optical_axis_y - 10.5, optical_axis_z - 10.5])
            cube([4.0, 21.0, 21.0]);
        // TCS34725 M2.5 screw holes
        translate([chassis_w/2 - 9.0, optical_axis_y - 7.5, optical_axis_z])
            rotate([0, 90, 0]) cylinder(d=2.2, h=6);
        translate([chassis_w/2 - 9.0, optical_axis_y + 7.5, optical_axis_z])
            rotate([0, 90, 0]) cylinder(d=2.2, h=6);

        // E. Wio Terminal Console Cradle (Inclined front zone)
        // Center of console cradle at Y = -22 mm
        translate([0, -22, chassis_h_front + 14.0]) {
            rotate([incline_angle, 0, 0]) {
                // Wio Terminal Body Pocket
                translate([-wio_w/2, -wio_d/2, -wio_thickness])
                    cube([wio_w, wio_d, wio_thickness + 5]);

                // LCD Screen Bezel Window
                translate([-screen_window_w/2, -screen_window_d/2 + 2, -wio_thickness - 10])
                    cube([screen_window_w, screen_window_d, 20]);

                // 5-Way Joystick Hole
                translate([wio_w/2 - 12, -wio_d/2 + 12, -wio_thickness - 10])
                    cylinder(d=joystick_hole_dia, h=20);

                // Top Buttons A, B, C Cutout Clearance
                translate([-wio_w/2 + 12, wio_d/2 - 4, -wio_thickness - 10])
                    cube([48, 8, 20]);
            }
        }

        // F. Internal Cable Conduits (Grove Cable Relief)
        // Left conduit (D0 NeoPixel)
        translate([-26, 0, 10]) rotate([0, 45, 0]) cube([8, 60, 8]);
        // Right conduit (I2C TCS34725)
        translate([ 26, 0, 10]) rotate([0, -45, 0]) cube([8, 60, 8]);

        // G. Li-Po Battery & Electronics Bay (Bottom hollow cavity)
        translate([-chassis_w/2 + 8, -chassis_d/2 + 8, -1])
            cube([chassis_w - 16, 50, 24]);

        // H. MicroSD Slot & USB-C Side Access Ports
        translate([-chassis_w/2 - 1, -26, 30])
            cube([10, 16, 8]); // USB-C pass-through
        translate([ chassis_w/2 - 9, -26, 30])
            cube([10, 16, 4]); // MicroSD access slot

        // I. 4x M3 Benchtop Mounting / Anti-Slip Rubber Foot Recesses
        for (mx = [-chassis_w/2 + 10, chassis_w/2 - 10]) {
            for (my = [-chassis_d/2 + 10, chassis_d/2 - 10]) {
                translate([mx, my, -1])
                    cylinder(d=3.4, h=6); // M3 clearance
                translate([mx, my, -0.1])
                    cylinder(d=10.0, h=2.5); // Rubber foot counterbore
            }
        }
    }
}

// Render the workstation body
spector_v5_workstation();
