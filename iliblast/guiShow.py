from config import *
from geometry import *

class guiShow:
    def __init__(self,gui,core):

        self.core = core
        self.Glist = {}
        #self.SetBackgroundColour('#EDFAFF')
        self.groups={
            'Model':[0,['Plane',['X','Y','Z']],['Layer',['___']],
                ['Tstep',['_____']],'Grid','Map'], #,'Variable'],
            'Flow':[1,'Head','Wcontent','Veloc-vect','Veloc-magn','Particles'],
            'Transport':[2,'Tracer'],
            'Chemistry':[3,['Species',['_______']],
                     ['Units',['mol/L','mmol/L','umol/L','nmol/L']],
                     ['User',['_______']]],
            'Observation':[4,['Type',['Profile','Breakthrough','XYplot']],
                           ['Zone',['_______']]]}
        self.dicVisu = {'Model':{'Plane':'Z','Layer':0,'Tstep':0,'Grid':False,'Map':False,'Variable':False},
                'Flow':{'Head':False,'Wcontent':False,'Veloc-vect':False,'Veloc-magn':False,'Particles':False},
                'Transport':{'Tracer':False},
                'Chemistry':{'Species':False,'Units':'mmol/L','User':False},
                'Observation':{'Type':'Profile','Zone':' '}}
        self.change={'Grid':None,'Veloc-vect':['scale',1.],
            'Particles':['time',10.],
            'Visible':['size',10]} # change that are not contours
        self.Vtypes = {'Modif':['Plane','Layer','Tstep','Units'],
            'Array' : ['Head','Wcontent','Veloc-magn','Tracer','Species','User'],
            'Image': ['Variable','Map'],'Grid':['Grid'],'Particles':['Particles'],
            'Vector' : ['Veloc-vect']}
        self.gui,self.visu = gui,gui.visu
        cfg = Config(self.core)
        self.gtyp = cfg.gtyp
        if self.gtyp=='wx': 
            self.dlgShow = cfg.show.Show(self,self.gui,self.core)
        elif self.gtyp=='qt': 
            self.dlgShow = gui.dlgShow
        self.dialogs = cfg.dialogs
        self.init()
        
    def init(self):     
        self.swiImg = 'Contour'
        self.userSpecies,self.data = {},None
        self.visu.Glist = self.Glist
        self.curVar, self.curVarView = {},None

    def getCurrentTime(self): return self.dlgShow.getCurrentTime()
    def getNames(self,nameBox): return self.dlgShow.getNames(nameBox)
    def setNames(self,nameBox,names,opt='strings'): 
        self.dlgShow.setNames(nameBox,names,opt)
    def setChemSpecies(self,specList):
        self.setNames('Chemistry_Species_L',specList)
    def setUserSpecies(self,dicU): self.userSpecies = dicU

    def getGlist(self,group,name):
        #print 'guish 55',group,name,self.Glist
        if self.Glist.has_key(group):
            if self.Glist[group].has_key(name): return self.Glist[group][name] 
            else :
                self.Glist[group][name] = {'value':None,'color':None,'calc':False}
        else :
            self.Glist[group] = {}
            self.Glist[group][name] = {'value':None,'color':None,'calc':False}
        return self.Glist[group][name] 
    
    def setGlistParm(self,group,name,parm,value):
        #print 'guish 67', group,name,parm, value
        self.Glist[group][name][parm]= value
        
    def resetGlist(self):
        """reset all Glist tags 'calc' to False"""
        for group in self.Glist.keys():
            for name in self.Glist[group].keys(): 
                self.Glist[group][name]['calc'] = False

    def onClick2(self,group,name,retour):
        """after the click the type of object is defined and data are retrieved 
        according to what has been typed
        group is the box, name is the item and retour is wether a boolean
        for a tickbox or the name of the item for a list
        the time and species has been stored previously (in onclick below)
        there are four types of action : 
          -  if a False arrives in retour just make the object unvisible. 
          - for observation go elsewhere to show the observations
          - if plane, time has changed show the same object but for different time
          - for the other case show the object
        objects : grid (true/false), vectors(true/false), map(true/false)
        variable (?), contour(group,name):True/false, types in Vtypes
        """
        #current visu data are stored (by wx dialog) in dicVisu
        listSpecies = self.getNames('Chemistry_Species_L')
        opt,bool = 'contour',False
        # set the first steps GRID, MAP, VARIABLE, PARTICLE
        m = self.dicVisu['Model']
        plane, layer, tstep = m['Plane'],m['Layer'],m['Tstep'];
        self.Tstep = tstep
        self.visu.drawObject('Grid',self.dicVisu['Model']['Grid'])
        if m['Variable'] : 
            self.visu.createImage(self.getCurrentVariable(plane,layer))
            m['Map'] = False
        elif m['Map'] : 
            self.visu.drawObject('Map',True)
        else :
            self.visu.drawObject('Image',False)
        self.visu.drawObject('Particles',self.dicVisu['Flow']['Particles'])
        # find the current CONTOUR and if needs to be dranw
        self.dlgShow.uncheckContours()
        Cgroup,Cname,species = self.getCurrentContour();#print 'guish l 94',group,name,species
        self.curName,self.curSpecies = Cname,species;# OA 10/5/17
        if group=='Observation': # observation for the group that is currently drawn
            if name=='Zone': self.onObservation(Cgroup,tstep)
            return
        # get the data for contours
        dataM = None
        #print 'guish 116', name,species,self.userSpecies
        if Cgroup != None : 
            self.arr3 = self.getArray3D(Cgroup,Cname,tstep,species)
            if species in self.userSpecies.keys():
                dataM = self.getUserSpecies(species,plane,layer)
            else :
                dataM = self.getArray2D(Cgroup,self.arr3,plane,layer)
        self.data = dataM;#print 'guish 113',shape(dataM)
        # get VECTORS
        dataV = None
        if self.dicVisu['Flow']['Veloc-vect']: 
            dataV = self.getVectors(plane,layer,tstep)
            opt = 'vector'
        #print self.dicVisu
        toshow = species
        if type(species)==type(bool): toshow = Cname # 28/3/17 oa to keep contour values for 
        glist = self.getGlist(Cgroup,toshow)
        value,color = glist['value'],glist['color'];#print 'guishow 122',Cgroup,Cname,value,color
        if layer !=0 : self.visu.changeAxesOri(plane)
        self.visu.curLayer = layer
        self.visu.createAndShowObject(dataM,dataV,opt,value,color)

    def resetDicContour(self):
        # put all cntour values to non
        for k in self.dicVisu.keys():
            for k1 in self.dicVisu[k].keys():
                if k1 in self.Vtypes['Array']:
                    self.dicVisu[k][k1] = False
 
    def getCurrentContour(self):   
        #returns the contour that is currently visible
        for k in self.dicVisu.keys():
            for k1 in self.dicVisu[k].keys():
                if k1 in self.Vtypes['Array']:
                    if self.dicVisu[k][k1] != False :  
                        return k,k1,self.dicVisu[k][k1]
        return None,None,None
        
    def getArray3D(self,group,name,tstep,spec):
        """get an array of data in the files written by a model, using the reader"""
        #print group,name,tstep
        arr = None
        if group=='Flow':
            if name=='Head':
                arr = self.core.flowReader.readHeadFile(self.core,tstep)
            elif name=='Wcontent':
                arr = self.core.flowReader.readWcontent(self.core,tstep)
            elif name=='Veloc-magn':
                vx,vy,vz = self.core.flowReader.readFloFile(self.core,tstep)
                if vz !=None:
                    arr=sqrt((vx[:,:,1:]/2+vx[:,:,:-1]/2)**2+(vy[:,1:,:]/2+vy[:,:-1,:]/2)**2+(vz[1:,:,:]/2+vz[:-1,:,:]/2)**2)
                else :
                    arr=sqrt((vx[:,:,1:]/2+vx[:,:,:-1]/2)**2+(vy[:,1:,:]/2+vy[:,:-1,:]/2)**2)
                #arr = arr[:,-1::-1,:] already done in flofile
        if group=='Transport':
            if name=='Tracer':
                arr = self.core.transReader.readUCN(self.core,'Mt3dms',tstep,0,'Tracer') #iesp=0
        if group=='Chemistry':
            if name=='Species':
                iesp = self.getNames('Chemistry_Species_L').index(spec)
                arr = self.core.transReader.readUCN(self.core,'Pht3d',tstep,iesp,spec) #iesp=0
        modgroup = self.core.dicaddin['Model']['group']
        #if modgroup[:4] =='Modf' and arr != None: arr= arr[:,-1::-1,:]
        #print 'guisho 154 arr3', shape(arr)
        return arr
        
    def getArray2D(self,group,arr3,plane,section):
        #print group,plane,section,shape(arr3),self.Species,self.Units
        X,Y = getXYmeshSides(self.core,plane,section)# X,Y can be in Z for presention purpose
        self.Umult, units = 1.,self.dicVisu['Chemistry']['Units']
        if group =='Chemistry':
            if self.dicVisu['Chemistry']['Species'] not in ['pH','ph','pe']:
                if units == 'mmol/L': self.Umult = 1000.
                elif units == 'umol/L': self.Umult = 1e6
                elif units == 'nmol/L': self.Umult = 1e9 
        modgroup = self.core.addin.getModelGroup()
        if self.swiImg =='Contour': 
            X=(X[:,:-1]+X[:,1:])/2;X=X[1:,:]
            Y=(Y[:-1,:]+Y[1:,:])/2;Y=Y[:,1:]
        if self.core.addin.getDim() in ['Radial','Xsection']:
            if modgroup[:4]=='Modf': 
                if self.core.addin.getModelType()=='free' and self.curName=='Head':
                    Y = self.getXyHeadFree(arr3,Y)
                return X,Y,arr3[::-1,0,:]*self.Umult
            else : 
                return X,Y,arr3[:,0,:]*self.Umult
        else : # 2 or 3D
            if modgroup=='Opgeo':
                return None,None,arr3[0]
            else :
                if plane=='Z': data = (X,Y,arr3[section,:,:]*self.Umult) #-1 for different orientation in modflow and real world
                elif plane=='Y': data = (X,Y,arr3[:,section,:]*self.Umult)
                elif plane=='X': data = (X,Y,arr3[:,:,section]*self.Umult)
                return data
                
    def getPointValue(self,x,y):
        """using a coordinate get the value of the current variable at
        this coordinates, using self.data which is a 2D array
        or """
        modgroup = self.core.addin.getModelGroup()
        if self.data == None or x==None or y==None or modgroup in ['Fipy','Opgeo']: 
            return ' '
        x0,y0 = self.data[0][0,:],self.data [1][:,0]
        d=x-x0; d1=d[d>0.]
        if len(d1)==0 : return ' '
        ix=where(d==amin(d1))[0][0]
        d=y-y0; d1=d[d>0.]
        if len(d1)==0 : return ' '
        iy=where(d==amin(d1))[0][0]
        if self.dicVisu['Model']['Variable'] and self.curVarView != None:
            zvalue = str(self.curVarView[iy,ix])[:6]
        else :
            zvalue = str(self.data[2][iy,ix])[:6]
        return zvalue
            
    def getXyHeadFree(self,arr3,Y):
        """modifies the Y coord to show the elevation of the water table
        for cases or radial and xsection. !Y not in the same dir as head"""
        nl,ny,nc = shape(arr3)
        dy=Y[-1,0]-Y[-2,0]
        for ic in range(nc):
            nbl0 = len(where(arr3[:,0,ic]==0)[0]);#print ic,nbl0
            if nbl0>0: 
                Y[nl-nbl0-1,ic] = arr3[nbl0,0,ic]
                Y[nl-nbl0,ic] = Y[nl-nbl0-1,ic]+dy/5
        return Y
        
            
    def getUserSpecies(self,name,plane,layer):
        formula0=self.userSpecies[name]
        formula1 = formula0*1
        species = self.getNames('Chemistry_Species_L')
        tsp = str(self.Tstep)
        for e in species:
            if e in formula0: 
                rp ='self.getArray3D(\'Chemistry\',\'Species\','+tsp+',\''+e+'\')'
                formula1 = formula1.replace(e,rp)
        exec('arr3 ='+formula1);#print arr3
        return self.getArray2D('Chemistry',arr3,plane,layer)        
        
    def get3Dvectors(self,tstep):
        mod = self.gui.varBox.parent.currentModel
        qx,qy,qz = self.core.flowReader.readFloFile(self.core,tstep);
        if mod=="Modflow":
            qx = qx[:,:,1:]/2+qx[:,:,:-1]/2
            qy = qy[:,1:,:]/2+qy[:,:-1,:]/2
            if qz !=None: qz = qz[1:,:,:]/2+qz[:-1,:,:]/2
        return qx,qy,qz
        
    def getVectors(self,plane,layer,tstep):
        X,Y = getXYmeshCenters(self.core,plane,layer);#print shape(X),shape(Y)
        qx,qy,qz = self.get3Dvectors(tstep)
        if self.core.addin.getDim() =='3D':
            if plane=='Z':
                U=qx[layer]
                V=qy[layer]
        elif self.core.addin.getDim() =='2D':
            U=qx[0]
            V=qy[0]
        elif self.core.addin.getDim() in ['Radial','Xsection']:
            U=qx[:,0,:]
            V=qz[:,0,:]            
        return X,Y,U,V
            
    def getCurrentVariable(self,plane,section):
        mod = self.gui.varBox.parent.currentModel
        line = self.gui.varBox.parent.currentLine
        media, opt, iper = 0,None,0; #print 'guisho 275',line,self.curVar
        if self.curVar.has_key(line): 
            mat = self.curVar[line]*1
        else:
            mat = self.core.getValueLong(mod,line,0)*1;#print 'show 260',shape(mat)
            self.curVar[line] = mat*1
        X,Y = getXYmeshSides(self.core,plane,section)
        if self.core.addin.getModelGroup()=='Opgeo':
            return None,None,mat[0][0]
        if self.core.addin.getDim() not in ['Radial','Xsection']:
            if plane=='Z': m2 = mat[section,:,:] #-1 for different orientation in modflow and real world
            elif plane=='Y': m2 = mat[:,section,:]
            elif plane=='X': m2 = mat[:,:,section]
        else :
            m2 = mat[-1::-1,0,:]
        self.curVarView = m2
        return X,Y, m2
        
    def onObservation(self,group,tstep):
        if group not in ['Flow','Transport','Chemistry']: 
            self.dialogs.onMessage(self.gui,'choose one variable')
            return
        item = self.dlgShow.FindWindowByName('Observation_Type_L')
        typ = item.GetStringSelection()[0]  # B P or X
        if group=='Chemistry': lesp=self.getNames('Chemistry_Species_L');
        elif group=='Flow': lesp=['Head','Flux','Wcontent']
        else : lesp=['Transport']
        data=zip(lesp,['Check']*len(lesp),[False]*len(lesp))
        #dialog to choose species to plot
        if len(lesp)>1: 
            dlg = self.dialogs.genericDialog(self.gui,'species',data)
            lst1=dlg.getValues()
            if lst1 != None:
                lst2=[]
                for i in range(len(lst1)): 
                    if lst1[i] : lst2.append(lesp[i])
                lesp = lst2
            else :return
        #dialog to choose layers if in 3D
        layers = 0
        if self.core.addin.getDim()=='3D':
            data = [('Layers (1, 3-6)','Text','')]
            dlg = self.dialogs.genericDialog(self.gui,'Select',data)
            d = dlg.getValues() #dialog to choose type of graph
            if d != None:
                layers=d[0]
            else :return            
        # dialog for type of graph, for flow this dialog is useless
        if group in ['Chemistry','Transport']: lst0 = ['Value','Weighted value','Mass Discharge (Md)','Mass Flux (J)']
        else : lst0 = ['Value','Weighted value','Flow (Q)','Darcy Flux (q)']
        data=[('Type','Choice',('Value',lst0))]
        dlg = self.dialogs.genericDialog(self.gui,'Select',data)
        d = dlg.getValues() #dialog to choose details
        if d != None:
            val=d[0]
            typ+=str(lst0.index(val));
        else : return

        item = self.dlgShow.FindWindowByName('Observation_Zone_L')
        znam = item.GetStringSelection()
        dist,val,lab = self.core.onPtObs(typ,tstep,group,znam,lesp,layers);#print 'guishow 263',val
        plt = self.dialogs.plotxy(self.gui,-1);plt.Show(True)
        if typ[0]=='X': plt.draw(dist,val,lab[1:],znam,lab[0],"val",typ='+');
        else : plt.draw(dist,val,lab[1:],znam,lab[0],"val");
        plt.Raise()
