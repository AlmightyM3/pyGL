import numpy

class OBJ:
    def __init__(self, path):
        vertPos = []
        texCords = []
        normals = []
        faces = []
        for line in open(path, "r"):
            values = line.split()
            match values[0]:
                case "o":
                    self.name = values[1]
                case "v":
                    vertPos.append([float(i) for i in values[1:]])
                case "vt":
                    texCords.append([float(i) for i in values[1:]])
                case "vn":
                    normals.append([float(i) for i in values[1:]])
                case "f":
                    if len(values[1:]) == 3:
                        faces.extend(values[1:])
                    elif len(values[1:]) > 3:
                        faces.extend(self.triangulateConvex(values[1:]))
        
        self.vertices = numpy.zeros(len(faces)*8,dtype=numpy.float32)
        for i in range(len(faces)):
            face = faces[i].split("/")
            self.vertices[i*8+0] = vertPos[int(face[0])-1][0]
            self.vertices[i*8+1] = vertPos[int(face[0])-1][1]
            self.vertices[i*8+2] = vertPos[int(face[0])-1][2]

            self.vertices[i*8+3] = normals[int(face[2])-1][0]
            self.vertices[i*8+4] = normals[int(face[2])-1][1]
            self.vertices[i*8+5] = normals[int(face[2])-1][2]

            self.vertices[i*8+6] = texCords[int(face[1])-1][0]
            self.vertices[i*8+7] = texCords[int(face[1])-1][1]

        self.indices = numpy.array(range(len(faces)),dtype=numpy.uint32) # need to fix so thare are no duplcits in self.vertices

    def triangulateConvex(self, face):
        triangles = []
        for i in range(1, len(face) - 1):
            triangles.extend([face[0], face[i], face[i + 1]])
        return triangles