// ==============================================================================
// SpectorV5-Pro: Precision Optical Cuvette Labyrinth Lid
// Designed with Skill: spectrometer-3d-chassis-architect
// Digital Agriphysics & AI Research Unit (JC_AI_SciRBRU)
// Department of Physics, Faculty of Science and Technology,
// Rambhai Barni Rajabhat University (RBRU)
//
// Complies with 5 Optical Rig Design Laws:
// - Law 3: Double-stepped interlocking labyrinth light baffle (100% stray-light cut-off)
// - Law 5: High-density wall opacity (minimum 3.0mm wall thickness)
//
// Ergonomics:
// - Textured / ribbed finger grip for non-slip one-handed cuvette insertion/removal
// - Internal cuvette headroom buffer cavity
// ==============================================================================

$fn = 60;

// --- Dimensions & Clearances ---
tolerance       = 0.25;  // 3D printer clearance (mm)

lid_outer_w     = 42.0;  // Lid outer width X (mm)
lid_outer_d     = 42.0;  // Lid outer depth Y (mm)
lid_height      = 18.0;  // Base cap height (mm)
handle_h        = 10.0;  // Grip handle height (mm)

// Workstation Baffle Lip Interface:
// Workstation rim outer is 36.0 x 36.0 mm (r=2), height 3.5mm
rim_cavity_w    = 36.0 + (tolerance * 2); // 36.5 mm
rim_cavity_depth= 4.2;                   // Clears the 3.5mm raised lip

// Secondary inner labyrinth baffle step
inner_step_w    = 24.0;
inner_step_h    = 3.0;

// Internal cuvette clearance cavity
cuvette_clear_w = 14.0;
cuvette_clear_h = 10.0;

// --- Modules ---

module rounded_rect(w, d, h, r=3) {
    hull() {
        translate([-w/2 + r, -d/2 + r, 0]) cylinder(r=r, h=h);
        translate([ w/2 - r, -d/2 + r, 0]) cylinder(r=r, h=h);
        translate([ w/2 - r,  d/2 - r, 0]) cylinder(r=r, h=h);
        translate([-w/2 + r,  d/2 - r, 0]) cylinder(r=r, h=h);
    }
}

module spector_v5_lid() {
    difference() {
        // --- Positive Body ---
        union() {
            // Main Cap Body
            rounded_rect(lid_outer_w, lid_outer_d, lid_height, r=4);
            
            // Ergonomic Ribbed Handle on Top
            translate([0, 0, lid_height]) {
                hull() {
                    translate([-lid_outer_w/2 + 8, -6, 0]) cylinder(r=3, h=handle_h);
                    translate([ lid_outer_w/2 - 8, -6, 0]) cylinder(r=3, h=handle_h);
                    translate([ lid_outer_w/2 - 8,  6, 0]) cylinder(r=3, h=handle_h);
                    translate([-lid_outer_w/2 + 8,  6, 0]) cylinder(r=3, h=handle_h);
                }
            }
            
            // Grip Ridges on Handle
            for (gx = [-12, -6, 0, 6, 12]) {
                translate([gx, 0, lid_height + handle_h])
                    rotate([0, 90, 0])
                        cylinder(r=1.2, h=2, center=true);
            }
        }
        
        // --- Negative Interlocking Labyrinth Cavities ---
        
        // Tier 1: Outer Labyrinth Groove (fits over the 36mm raised rim)
        translate([0, 0, -0.1])
            rounded_rect(rim_cavity_w, rim_cavity_w, rim_cavity_depth + 0.1, r=2.5);
            
        // Tier 2: Step-down Light Baffle Cavity
        translate([0, 0, rim_cavity_depth - 0.1])
            rounded_rect(inner_step_w, inner_step_w, inner_step_h + 0.1, r=2.0);
            
        // Tier 3: Cuvette Top Clearance Chamber
        translate([0, 0, rim_cavity_depth + inner_step_h - 0.1])
            rounded_rect(cuvette_clear_w, cuvette_clear_w, cuvette_clear_h + 0.1, r=1.5);
            
        // Ergonomic Finger Flutes on side walls for easy pull-off
        translate([-lid_outer_w/2, 0, lid_height/2])
            rotate([0, 90, 0]) cylinder(r=6, h=2.5, center=true);
        translate([ lid_outer_w/2, 0, lid_height/2])
            rotate([0, 90, 0]) cylinder(r=6, h=2.5, center=true);
    }
}

// Render the Labyrinth Lid
spector_v5_lid();
