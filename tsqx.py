##########
## TSQX ##
##########

# original TSQ by evan chen

import sys
import string
import argparse

fn_names = {
    'circumcenter' : 3,
    'orthocenter' : 3,
    'incircle' : 3,
    'circumcircle' : 3,
    'centroid' : 3,
    'incenter' : 3,
    'midpoint' : 1,
    'extension' : 4,
    'foot' : 3,
    'CP' : 2,
    'CR' : 2,
    'dir' : 1,
    'intersect': 2,
    'IP': 2,
    'OP': 2,
    'Line': 2,
    'bisectorpoint': 2,
    'rightanglemark': 3,
    'anglemark': 3,
    'arc': 4,
    'shift': 1,
    'xscale': 1,
    'yscale': 1,
    'scale': 1,
    'rotate': 2,
    'reflect': 2,
    'tangent': 3,
    'pathticks': 2,
    }
short_names = {
    'circle' : 'circumcircle',
    'rightangle' : 'rightanglemark',
    }
polygons = {
    'acute' : ['dir(110)', 'dir(210)', 'dir(330)'],
    'triangle' : ['dir(110)', 'dir(210)', 'dir(330)'],
    'obtuse' : ['dir(100)', 'dir(170)', 'dir(10)'],
    'isosceles' : ['dir(90)', 'dir(230)', 'dir(310)'],
    'equilateral' : ['dir(90)', 'dir(210)', 'dir(330)'],
    'cyclicquad' : ['dir(150)', 'dir(200)', 'dir(340)', 'dir(70)'],
    'quadrilateral' : ['dir(150)', 'dir(200)', 'dir(340)', 'dir(70)'], # should make this non-cyclic
    'cyclic' : ['generate'],
    'regular' : ['generate'],
    }

# The following is really bad
for letter in string.ascii_uppercase:
  fn_names['-%s+2*foot' %letter] = 3

def autoParen(tokens):
  if len(tokens) == 0: return ''
  else: t = tokens.pop(0)

  # command overloading
  if t[:-1].strip() in short_names or t[:-1].strip() in fn_names:
    nargs = int(t[-1])
    t = t[:-1].strip()
    if t in short_names:
      t = short_names[t]
    if t in fn_names:
      args = [autoParen(tokens) for i in range(nargs)]
      return t + '(' + ', '.join(args) + ')'
    else:
      return t
  else:
    if t in short_names:
        t = short_names[t]
    if t in fn_names:
        nargs = fn_names[t]
        args = [autoParen(tokens) for i in range(nargs)]
        return t + '(' + ', '.join(args) + ')'
    else:
      return t

def generatePoints(poly_name, num_sides):
  if poly_name == 'cyclic':
    if num_sides == 3:
      return ['dir(110)', 'dir(210)', 'dir(330)']
    elif num_sides == 4:
      return ['dir(150)', 'dir(200)', 'dir(340)', 'dir(70)']
    else:
      points = [] 
      for i in range(num_sides):
        angle = 90.0 + i * 360.0 / num_sides
        if angle > 360: angle -= 360
        points.append('dir(' + str(angle) + ')')
      return points # should make this non-regular
  elif poly_name == 'regular':
    if num_sides == 3:
      return ['dir(90)', 'dir(210)', 'dir(330)']
    else:
      points = []
      for i in range(num_sides):
        angle = 90.0 + i * 360.0 / num_sides
        if angle > 360: angle -= 360
        points.append('dir(' + str(angle) + ')')
      return points

# argument parsing
parser = argparse.ArgumentParser(description='Generate a diagram.')
parser.add_argument('-p', '--pre',
    help = 'Adds an Asymptote preamble.',
    action = 'store_true',
    dest = 'preamble',
    default = False)
parser.add_argument('-n', '--no-trans',
    help = 'Temporarily disables the transparencies.',
    action = 'store_true',
    dest = 'notrans',
    default = False)
parser.add_argument('fname',
    help = 'If provided, reads from the designated file rather than stdin',
    metavar = "filename",
    nargs = '?',
    default = '')
parser.add_argument('-s', '--size',
    help = 'If provided, sets the image size in the preamble. (Use with -p.)',
    action = 'store',
    dest = 'size',
    default = '8cm')
parser.add_argument('-sl', '--soft-label',
    help = 'Does not mark points, only labels them.',
    action = 'store_true',
    dest = 'softlabel',
    default = False)
args = parser.parse_args()


# Initialize some stuff
raw_code = ""
dot_code = ""

if args.preamble:
  print("import olympiad;")
  print("import cse5;")
  print("size(%s);" %args.size)
  print("defaultpen(fontsize(9pt));")
  print("settings.outformat=\"pdf\";")
if args.fname is not '':
  stream = open(args.fname, 'r')
else:
  stream = sys.stdin


in_comment_mode = False
# Print output
for line in stream:
  raw_code += line
  line = line.strip()

  # Empty line = newspace
  if line == "":
    print("")
    continue

  # Handling of comments
  if line[:2] == "//":
    print(line)
    continue
  if line[:2] == "/*" and line[-2:] == "*/":
    print(line)
    continue
  elif line[:2] == "/*":
    in_comment_mode = True
    print(line)
    continue
  elif in_comment_mode and line[-2:] == "*/":
    in_comment_mode = False
    print("*/")
    continue

  if in_comment_mode:
    print(line)
    continue

  # Verbatim
  if line[0] == "!":
    print(line[1:].strip())
    continue

  # Decide whether to auto-paren
  if line[0] == ".":
    # Force auto paren
    do_auto_paren = True
    line = line[1:].strip()
  elif line[0] == ">":
    do_auto_paren = False
    line = line[1:].strip()
  else:
    do_auto_paren = not (',' in line) # just default to auto-ing unless , appears

  # preset polygons
  if line[0] == "~":
    line = line[1:].strip()
    point_names = line.split(" ")
    poly_name = point_names.pop(0)
    point_coords = polygons[poly_name]

    if point_coords[0] == "generate":
      point_coords = generatePoints(poly_name, len(point_names))

    for i in range(len(point_names)):
      label_name = point_names[i]
      expr = point_coords[i]

      if len(label_name) > 0 and label_name[-1] == ":":
        draw_point = False
        label_point = False
        force_dot = False
        label_name = label_name[:-1].strip()
      elif len(label_name) > 0 and label_name[-1] == ".":
        draw_point = True
        label_point = False
        force_dot = False
        label_name = label_name[:-1].strip()
      elif len(label_name) > 0 and label_name[-1] == ";": # force dot label
        draw_point = True
        label_point = True
        force_dot = True
        label_name = label_name[:-1].strip()
      else:
        draw_point = True
        label_point = True
        force_dot = False
      label_name = label_name.strip()
      point_name = label_name.replace("'", "p") # primes

      direction = "dir(" + point_name + "-origin)"

      if point_name != "":
        print("pair %s = %s;" %(point_name, expr))
      if draw_point:
        if label_point:
          if (args.softlabel and not force_dot):
            dot_code += "label(\"$%s$\", %s, %s);\n" %(label_name, point_name, direction)
          else:
            dot_code += "dot(\"$%s$\", %s, %s);\n" %(label_name, point_name, direction)
        else:
          dot_code += "dot(%s);\n" %(point_name if point_name else expr)

  elif "=" in line:
    label_name, raw_expr = line.split("=", 2)

    if len(label_name) > 0 and label_name[-1] == ":":
      draw_point = False
      label_point = False
      force_dot = False
      label_name = label_name[:-1].strip()
    elif len(label_name) > 0 and label_name[-1] == ".":
      draw_point = True
      label_point = False
      force_dot = False
      label_name = label_name[:-1].strip()
    elif len(label_name) > 0 and label_name[-1] == ";":
      draw_point = True
      label_point = True
      force_dot = True
      label_name = label_name[:-1].strip()
    else:
      draw_point = True
      label_point = True
      force_dot = False
    label_name = label_name.strip()
    point_name = label_name.replace("'", "p") # primes

    if do_auto_paren:
      tokens = raw_expr.strip().split(' ')
      expr = autoParen(tokens)
      if len(tokens) == 0:
        direction = "dir(" + point_name + "-origin)"
      elif len(tokens) == 1:
        magnitude, angle = tokens[0].split("R", 2)
        direction = "dir(" + angle + ")"
        if magnitude != "":
          direction = magnitude + "*" + direction
    else:
      expr = raw_expr.strip()
      direction = "dir(" + point_name + "-origin)"

    if point_name != "":
      print("pair %s = %s;" %(point_name, expr))
    if draw_point:
      if label_point:
        if (args.softlabel and not force_dot) or (not args.softlabel and force_dot):
          dot_code += "label(\"$%s$\", %s, %s);\n" %(label_name, point_name, direction)
        else:
          dot_code += "dot(\"$%s$\", %s, %s);\n" %(label_name, point_name, direction)
      else:
        dot_code += "dot(%s);\n" %(point_name if point_name else expr)

  else:
    line = line.strip()
    pen = None
    if do_auto_paren:
      tokens = line.split(' ')
      expr = autoParen(tokens)
      # 0.2 mediumcyan / blue -> opacity(0.2)+mediumcyan, blue
      if '/' in tokens:
        tindex = tokens.index('/') # index of transparency divider
        if tokens[0][0] == "0": # first token is leading 0
          fillpen = "opacity(" + tokens[0] + ")"
          if tindex != 1:
            fillpen += '+' + '+'.join(tokens[1:tindex]) # add on others
        else:
          fillpen = '+'.join(tokens[0:tindex])
        drawpen = '+'.join(tokens[tindex+1:])
        if not drawpen: drawpen = "defaultpen"

        if args.notrans:
          print("draw(" + expr + ", " + drawpen + ");")
        else:
          print("filldraw(" + expr + ", " + fillpen + ", " + drawpen + ");")
      else:
        pen = '+'.join(tokens) # any remaining tokens
    else:
      expr = line # you'll have to put commas here for pens manually
      pen = ''
      
    if pen:
      print("draw(" + expr + ", " + pen + ");")
    elif pen is not None:
      print("draw(" + expr + ");")

print("\n" + dot_code)
print("/* Source generated by TSQX */")

stream.close()
