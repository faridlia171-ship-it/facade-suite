import { useState, useRef } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import { Badge } from '../components/ui/badge'
import { API_URL } from '../config'

interface MeasurementRef {
  type: 'agglo' | 'custom'
  width_cm: number
  height_cm: number
}

export default function Metrage() {
  const [selectedImage, setSelectedImage] = useState<string | null>(null)
  const [imageFile, setImageFile] = useState<File | null>(null)
  const [facadeCode, setFacadeCode] = useState<string>('A')
  const [quality, setQuality] = useState<'green' | 'orange' | 'red'>('green')
  const [refType, setRefType] = useState<'agglo' | 'custom'>('agglo')
  const [customRef, setCustomRef] = useState({ width: 20, height: 50 })
  const [measurements, setMeasurements] = useState<{ surface: number; perimeter: number } | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setImageFile(file)
      const reader = new FileReader()
      reader.onloadend = () => {
        setSelectedImage(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const calculateMeasurements = () => {
    // Simulation du calcul de métrage
    // Dans la version complète, ceci interagirait avec le backend pour le calcul réel
    const refWidth = refType === 'agglo' ? 20 : customRef.width
    const refHeight = refType === 'agglo' ? 50 : customRef.height
    
    // Calcul simulé (remplacer par l'API backend)
    const simulatedSurface = Math.random() * 100 + 50
    const simulatedPerimeter = Math.random() * 50 + 20
    
    setMeasurements({
      surface: parseFloat(simulatedSurface.toFixed(2)),
      perimeter: parseFloat(simulatedPerimeter.toFixed(2)),
    })
  }

  const saveMetrage = async () => {
    if (!imageFile || !measurements) return

    try {
      const formData = new FormData()
      formData.append('photo', imageFile)
      formData.append('facade_code', facadeCode)
      formData.append('quality', quality)
      formData.append('ref_type', refType)
      formData.append('ref_width', customRef.width.toString())
      formData.append('ref_height', customRef.height.toString())
      formData.append('surface', measurements.surface.toString())
      formData.append('perimeter', measurements.perimeter.toString())

      const token = localStorage.getItem('token')
      const response = await fetch(`${API_URL}/api/metrage/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      })

      if (response.ok) {
        alert('Métrage enregistré avec succès')
        resetForm()
      }
    } catch (error) {
      console.error('Error saving metrage:', error)
    }
  }

  const resetForm = () => {
    setSelectedImage(null)
    setImageFile(null)
    setMeasurements(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const getQualityColor = (q: string) => {
    switch (q) {
      case 'green': return 'bg-green-500'
      case 'orange': return 'bg-orange-500'
      case 'red': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Métrage Photo</h1>
        <p className="text-muted-foreground">
          Calculez les surfaces à partir de vos photos de chantier
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Photo de la façade</CardTitle>
            <CardDescription>
              Prenez une photo avec une référence visible (agglo ou règle)
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="facade">Façade</Label>
              <select
                id="facade"
                value={facadeCode}
                onChange={(e) => setFacadeCode(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                <option value="A">Façade A</option>
                <option value="B">Façade B</option>
                <option value="C">Façade C</option>
                <option value="D">Façade D</option>
              </select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="quality">Qualité de la photo</Label>
              <div className="flex gap-2">
                {(['green', 'orange', 'red'] as const).map((q) => (
                  <button
                    key={q}
                    type="button"
                    onClick={() => setQuality(q)}
                    className={`flex-1 h-10 rounded-md border-2 ${
                      quality === q ? 'border-primary' : 'border-input'
                    } ${getQualityColor(q)} transition-colors`}
                  >
                    <span className="text-white font-medium">
                      {q === 'green' ? 'Bonne' : q === 'orange' ? 'Moyenne' : 'Mauvaise'}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="photo">Photo</Label>
              <Input
                ref={fileInputRef}
                id="photo"
                type="file"
                accept="image/*"
                capture="environment"
                onChange={handleImageSelect}
              />
            </div>

            {selectedImage && (
              <div className="border rounded-lg overflow-hidden">
                <img
                  src={selectedImage}
                  alt="Façade"
                  className="w-full h-auto"
                />
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Référence de mesure</CardTitle>
            <CardDescription>
              Choisissez votre référence pour le calcul
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Type de référence</Label>
              <div className="flex gap-2">
                <Button
                  type="button"
                  variant={refType === 'agglo' ? 'default' : 'outline'}
                  onClick={() => setRefType('agglo')}
                  className="flex-1"
                >
                  Agglo 20×50
                </Button>
                <Button
                  type="button"
                  variant={refType === 'custom' ? 'default' : 'outline'}
                  onClick={() => setRefType('custom')}
                  className="flex-1"
                >
                  Personnalisé
                </Button>
              </div>
            </div>

            {refType === 'custom' && (
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="width">Largeur (cm)</Label>
                  <Input
                    id="width"
                    type="number"
                    value={customRef.width}
                    onChange={(e) => setCustomRef({ ...customRef, width: parseFloat(e.target.value) })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="height">Hauteur (cm)</Label>
                  <Input
                    id="height"
                    type="number"
                    value={customRef.height}
                    onChange={(e) => setCustomRef({ ...customRef, height: parseFloat(e.target.value) })}
                  />
                </div>
              </div>
            )}

            <div className="pt-4">
              <Button
                onClick={calculateMeasurements}
                disabled={!selectedImage}
                className="w-full"
              >
                Calculer le métrage
              </Button>
            </div>

            {measurements && (
              <div className="space-y-3 p-4 bg-muted rounded-lg">
                <div className="flex justify-between items-center">
                  <span className="font-medium">Surface totale</span>
                  <Badge variant="default" className="text-lg px-4 py-1">
                    {measurements.surface} m²
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="font-medium">Périmètre</span>
                  <Badge variant="secondary" className="text-lg px-4 py-1">
                    {measurements.perimeter} m
                  </Badge>
                </div>
                <Button onClick={saveMetrage} className="w-full mt-4">
                  Enregistrer
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <Card className="bg-blue-50 border-blue-200">
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <div className="text-2xl">ℹ️</div>
            <div className="space-y-1">
              <p className="font-medium text-blue-900">Note importante</p>
              <p className="text-sm text-blue-800">
                Facade Suite est un outil d'aide au métrage. Vous restez seul responsable 
                de la vérification finale des métrés. L'éditeur ne peut être tenu responsable.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
