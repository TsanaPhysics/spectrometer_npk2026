// ==============================================================================
// 🎨 QUANTUM PHYSICISTS CHIBI FIGURINE COLLECTION (PIXAR / GHIBLI STYLE)
// 🔬 Albert Einstein • Max Planck • Werner Heisenberg • Erwin Schrödinger
// 🏛️ หน่วยวิจัยฟิสิกส์เกษตรดิจิทัลและปัญญาประดิษฐ์ (AI4D AgriPhysics) มรภ.รำไพพรรณี
// ==============================================================================

$fn = 40; // Resolution for export (set to 24 for fast preview, 50 for final render)

// ------------------------------------------------------------------------------
// GLOBAL PARAMETERS (Chibi 1:2.5 Proportion)
// ------------------------------------------------------------------------------
total_height      = 100.0; // mm
plinth_width      = 55.0;  // mm
plinth_depth      = 45.0;  // mm
plinth_height     = 10.0;  // mm

head_radius_x     = 21.0;
head_radius_y     = 19.0;
head_radius_z     = 21.0;
head_center_z     = 62.0;

body_radius_x     = 14.0;
body_radius_y     = 12.0;
body_height       = 24.0;
body_center_z     = 36.0;

leg_radius        = 5.0;
leg_length        = 18.0;
leg_spread        = 8.5;

// ==============================================================================
// 1. BASE MODULES: PLINTH & CHIBI BODY RIG
// ==============================================================================

module chibi_plinth(name="Albert Einstein", formula="E = mc²") {
    difference() {
        union() {
            // Stepped wooden plinth base
            hull() {
                translate([-plinth_width/2, -plinth_depth/2, 0])
                    cylinder(r=3, h=4, $fn=16);
                translate([plinth_width/2, -plinth_depth/2, 0])
                    cylinder(r=3, h=4, $fn=16);
                translate([-plinth_width/2, plinth_depth/2, 0])
                    cylinder(r=3, h=4, $fn=16);
                translate([plinth_width/2, plinth_depth/2, 0])
                    cylinder(r=3, h=4, $fn=16);
            }
            translate([0, 0, 4])
                hull() {
                    translate([-plinth_width/2 + 3, -plinth_depth/2 + 3, 0])
                        cylinder(r=2, h=6, $fn=16);
                    translate([plinth_width/2 - 3, -plinth_depth/2 + 3, 0])
                        cylinder(r=2, h=6, $fn=16);
                    translate([-plinth_width/2 + 3, plinth_depth/2 - 3, 0])
                        cylinder(r=2, h=6, $fn=16);
                    translate([plinth_width/2 - 3, plinth_depth/2 - 3, 0])
                        cylinder(r=2, h=6, $fn=16);
                }
            // Brass nameplate plaque
            translate([0, -plinth_depth/2 + 1.5, 5])
                rotate([15, 0, 0])
                cube([plinth_width - 12, 2.5, 6], center=true);
        }
        // Bevel top edge slightly
    }
}

module chibi_lower_body() {
    // Left & Right Legs
    for (side = [-1, 1]) {
        translate([side * leg_spread, 0, 10]) {
            // Leg trousers
            cylinder(r1=leg_radius*1.1, r2=leg_radius*0.95, h=16);
            // Cute rounded shoe
            translate([0, 1.5, 0])
                scale([1.1, 1.4, 0.9])
                sphere(r=5.2);
        }
    }
}

module chibi_torso(jacket_type="sweater") {
    translate([0, 0, body_center_z]) {
        // Pear-shaped cute body
        scale([1, 0.88, 1])
            cylinder(r1=body_radius_x, r2=body_radius_x*0.75, h=body_height, center=true);
        
        // Belly softness
        translate([0, 2, -2])
            scale([1.05, 0.9, 0.95])
            sphere(r=body_radius_x*0.9);

        // Collar & tie / bowtie
        translate([0, 6, body_height/2 - 1]) {
            // Collar fold
            rotate([35, 0, 0])
                cube([10, 4, 3], center=true);
            if (jacket_type == "bowtie" || jacket_type == "suit") {
                // Cute Bowtie
                translate([0, 1.5, -2]) {
                    sphere(r=2);
                    translate([-3.2, 0, 0]) rotate([0, 20, 0]) cube([4, 2, 3], center=true);
                    translate([3.2, 0, 0]) rotate([0, -20, 0]) cube([4, 2, 3], center=true);
                }
            } else if (jacket_type == "tie") {
                // Necktie
                translate([0, 1.5, -5])
                    cube([3, 1.8, 8], center=true);
            }
        }
    }
}

module chibi_head_base() {
    // Oversized Pixar/Ghibli Head
    translate([0, 0, head_center_z]) {
        scale([head_radius_x, head_radius_y, head_radius_z] / 20)
            sphere(r=20);
        // Chubby cheeks
        translate([-11, 8, -4]) sphere(r=7.5);
        translate([11, 8, -4])  sphere(r=7.5);
        // Cute button nose
        translate([0, 18, -2])
            scale([1, 0.8, 0.8])
            sphere(r=3.2);
        // Cute ears
        translate([-head_radius_x - 1.5, 0, 0])
            rotate([0, 15, -10])
            scale([0.6, 0.9, 1.1])
            sphere(r=5.5);
        translate([head_radius_x + 1.5, 0, 0])
            rotate([0, -15, 10])
            scale([0.6, 0.9, 1.1])
            sphere(r=5.5);
    }
}

// Glasses Module
module chibi_round_spectacles(bridge_w=7, rim_r=6.5) {
    translate([0, 17.5, head_center_z]) {
        // Bridge
        translate([0, 0, 0])
            cube([bridge_w, 1.2, 1.5], center=true);
        // Left & Right wire rims
        for (side = [-1, 1]) {
            translate([side * (bridge_w/2 + rim_r - 0.5), 0, 0])
                rotate([90, 0, 0])
                difference() {
                    cylinder(r=rim_r, h=2, center=true);
                    cylinder(r=rim_r - 1.2, h=2.5, center=true);
                }
        }
    }
}

// ==============================================================================
// 2. CHARACTER MODULES (THE QUANTUM QUARTET)
// ==============================================================================

// ------------------------------------------------------------------------------
// A. ALBERT EINSTEIN (Wild Hair, Mustache, E=mc² Chalkboard)
// ------------------------------------------------------------------------------
module albert_einstein_chibi() {
    union() {
        chibi_plinth(name="Albert Einstein", formula="E = mc²");
        chibi_lower_body();
        chibi_torso(jacket_type="sweater");
        chibi_head_base();

        // 1. Wild fluffy curly hair (Multiple overlapping tufts)
        translate([0, 0, head_center_z]) {
            // Crown tufts
            for (ang = [-70:25:70]) {
                rotate([0, ang, 0])
                translate([0, -2, head_radius_z + 2])
                    sphere(r=6.5);
            }
            // Back & side curls
            for (a = [60:40:300]) {
                rotate([0, 0, a])
                translate([head_radius_x + 1, 0, 2])
                    scale([1.1, 1.1, 0.9])
                    sphere(r=7.0);
            }
            for (a = [90:50:270]) {
                rotate([0, 0, a])
                translate([head_radius_x + 3, 0, -6])
                    sphere(r=6.0);
            }
        }

        // 2. Iconic bushy mustache
        translate([0, 17.8, head_center_z - 6]) {
            scale([1.2, 0.9, 0.8]) {
                translate([-4.5, 0, -0.5]) rotate([0, 15, -10]) sphere(r=3.8);
                translate([4.5, 0, -0.5])  rotate([0, -15, 10]) sphere(r=3.8);
                sphere(r=3.0);
            }
        }

        // 3. Both Arms holding E = mc² Slate
        // Slate / Chalkboard
        translate([0, 15, body_center_z + 2]) {
            rotate([-12, 0, 0]) {
                // Wooden Frame
                cube([26, 3.5, 18], center=true);
                // Inner slate recessed
                translate([0, 0.5, 0])
                    cube([22, 3.0, 14], center=true);
            }
        }
        // Left & Right Arm
        for (side = [-1, 1]) {
            hull() {
                translate([side * 14, 2, body_center_z + 9]) sphere(r=4.5);
                translate([side * 11, 13, body_center_z + 1]) sphere(r=3.8);
            }
        }
    }
}

// ------------------------------------------------------------------------------
// B. MAX PLANCK (Distinguished Pince-Nez, Dark Suit & Glowing Quantum Orb)
// ------------------------------------------------------------------------------
module max_planck_chibi() {
    union() {
        chibi_plinth(name="Max Planck", formula="E = hν");
        chibi_lower_body();
        chibi_torso(jacket_type="bowtie");
        chibi_head_base();

        // 1. Neat distinguished parted hair & high bald forehead
        translate([0, 0, head_center_z]) {
            // Side & back hair fringe
            for (a = [80:30:280]) {
                rotate([0, 0, a])
                translate([head_radius_x - 1, 0, -2])
                    sphere(r=5.5);
            }
            // Parted hairline fringe
            translate([-head_radius_x/2, 10, head_radius_z - 4]) sphere(r=4);
            translate([head_radius_x/2, 10, head_radius_z - 4]) sphere(r=4);
        }

        // 2. Spectacles (Pince-Nez)
        chibi_round_spectacles(bridge_w=5, rim_r=6.0);

        // 3. Trim gentleman mustache
        translate([0, 17.5, head_center_z - 6.5]) {
            cube([10, 2.2, 2.5], center=true);
        }

        // 4. Arms cupping the Glowing Quantum Energy Orb (h*nu)
        translate([0, 16, body_center_z + 2]) {
            // Central Energy Quantum Orb
            sphere(r=6.5);
            // Orbital ring around quantum orb
            rotate([45, 30, 0])
                difference() {
                    cylinder(r=9.5, h=1.4, center=true);
                    cylinder(r=8.0, h=2, center=true);
                }
        }
        // Arms
        for (side = [-1, 1]) {
            hull() {
                translate([side * 14, 2, body_center_z + 9]) sphere(r=4.5);
                translate([side * 7, 14, body_center_z + 1]) sphere(r=3.8);
            }
        }
    }
}

// ------------------------------------------------------------------------------
// C. WERNER HEISENBERG (Wavy Hair, Suit & Uncertainty Orbital Ring)
// ------------------------------------------------------------------------------
module werner_heisenberg_chibi() {
    union() {
        chibi_plinth(name="Werner Heisenberg", formula="Δx·Δp ≥ ℏ/2");
        chibi_lower_body();
        chibi_torso(jacket_type="tie");
        chibi_head_base();

        // 1. Youthful sculpted wavy hair parted on left
        translate([0, 0, head_center_z]) {
            // Wavy hair crest
            translate([-3, 4, head_radius_z + 1])
                rotate([15, -10, 20])
                scale([1.3, 1.1, 0.9])
                sphere(r=8.0);
            translate([8, 2, head_radius_z - 1])
                rotate([10, 15, -15])
                scale([1.2, 1.0, 0.8])
                sphere(r=7.5);
            // Full back & side hair volume
            for (a = [60:35:300]) {
                rotate([0, 0, a])
                translate([head_radius_x, 0, 2])
                    sphere(r=6.0);
            }
        }

        // 2. Raised expressive hand holding Uncertainty Principle Cloud / Atom Orbital
        // Right hand presenting the quantum uncertainty orbital
        translate([14, 15, body_center_z + 8]) {
            // Central atomic core
            sphere(r=3.5);
            // 3 Intersecting Bohr/Heisenberg orbital rings
            rotate([20, 45, 0])
                difference() {
                    cylinder(r=10, h=1.2, center=true);
                    cylinder(r=8.6, h=1.8, center=true);
                }
            rotate([-35, -45, 25])
                difference() {
                    cylinder(r=10, h=1.2, center=true);
                    cylinder(r=8.6, h=1.8, center=true);
                }
            rotate([80, 10, -30])
                difference() {
                    cylinder(r=10, h=1.2, center=true);
                    cylinder(r=8.6, h=1.8, center=true);
                }
        }
        // Right Arm reaching forward
        hull() {
            translate([14, 2, body_center_z + 9]) sphere(r=4.5);
            translate([13, 11, body_center_z + 6]) sphere(r=3.8);
        }
        // Left Arm resting politely on side/hip
        hull() {
            translate([-14, 2, body_center_z + 9]) sphere(r=4.5);
            translate([-13, 6, body_center_z - 2]) sphere(r=3.8);
        }
    }
}

// ------------------------------------------------------------------------------
// D. ERWIN SCHRÖDINGER (Glasses, Sweater Vest, Box with Peeking Cat)
// ------------------------------------------------------------------------------
module erwin_schrodinger_chibi() {
    union() {
        chibi_plinth(name="Erwin Schrödinger", formula="iℏ ∂ψ/∂t = Ĥψ");
        chibi_lower_body();
        chibi_torso(jacket_type="bowtie");
        chibi_head_base();

        // 1. Neat swept-back intellectual hair
        translate([0, 0, head_center_z]) {
            for (ang = [-60:30:60]) {
                rotate([ang, 0, 0])
                translate([0, -head_radius_y + 4, head_radius_z - 3])
                    sphere(r=6.5);
            }
            for (a = [90:40:270]) {
                rotate([0, 0, a])
                translate([head_radius_x, 0, 0])
                    sphere(r=5.5);
            }
        }

        // 2. Intellectual round spectacles
        chibi_round_spectacles(bridge_w=6, rim_r=6.2);

        // 3. Schrödinger's Cat in a Box!
        translate([11, 15, body_center_z + 2]) {
            // Cardboard Box
            difference() {
                cube([18, 16, 14], center=true);
                translate([0, 0, 2])
                    cube([15.5, 13.5, 13], center=true);
            }
            // Flaps open
            translate([0, 8, 7]) rotate([-30, 0, 0]) cube([17, 4, 1.5], center=true);
            translate([0, -8, 7]) rotate([30, 0, 0]) cube([17, 4, 1.5], center=true);

            // Adorable Peeking Cat Head!
            translate([0, 0, 8]) {
                // Cat Head
                sphere(r=5.5);
                // Cute triangular ears
                translate([-3.2, 0, 4.5]) rotate([0, -25, 0]) cylinder(r1=2.8, r2=0.5, h=4.5, center=true);
                translate([3.2, 0, 4.5])  rotate([0, 25, 0])  cylinder(r1=2.8, r2=0.5, h=4.5, center=true);
                // Cute cat snout & nose
                translate([0, 4.5, -0.5]) sphere(r=1.8);
                // Little cat paws resting on front box rim
                translate([-4, 7.5, 0]) sphere(r=2.2);
                translate([4, 7.5, 0])  sphere(r=2.2);
            }
        }

        // Arms holding the box
        hull() {
            translate([14, 2, body_center_z + 9]) sphere(r=4.5);
            translate([13, 11, body_center_z + 1]) sphere(r=3.8);
        }
        hull() {
            translate([-14, 2, body_center_z + 9]) sphere(r=4.5);
            translate([2, 14, body_center_z + 1]) sphere(r=3.8);
        }
    }
}

// ------------------------------------------------------------------------------
// E. QUANTUM QUARTET DIORAMA (All 4 Side-by-Side)
// ------------------------------------------------------------------------------
module quantum_quartet_diorama() {
    translate([-85, 0, 0]) albert_einstein_chibi();
    translate([-28, 0, 0]) max_planck_chibi();
    translate([28, 0, 0])  werner_heisenberg_chibi();
    translate([85, 0, 0])  erwin_schrodinger_chibi();
}

// ==============================================================================
// RENDER SELECTION (Default: Grand Diorama or Individual Figurine)
// ==============================================================================
// Change selector: "diorama", "einstein", "planck", "heisenberg", "schrodinger"
character_selector = "diorama";

if (character_selector == "diorama") {
    quantum_quartet_diorama();
} else if (character_selector == "einstein") {
    albert_einstein_chibi();
} else if (character_selector == "planck") {
    max_planck_chibi();
} else if (character_selector == "heisenberg") {
    werner_heisenberg_chibi();
} else if (character_selector == "schrodinger") {
    erwin_schrodinger_chibi();
}
