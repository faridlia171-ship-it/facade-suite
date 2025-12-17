import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import { Badge } from '../components/ui/badge'
import { Textarea } from '../components/ui/textarea'
import { API_URL } from '../config'

interface QuoteLine {
  id?: string
  label: string
  quantity: number
  unit_price: number
  total: number
}

interface Quote {
  id: string
  project_id: string
  status: string
  current_version: number
  total: number
  created_at: string
  lines: QuoteLine[]
}

export default function Quotes() {
  const [quotes, setQuotes] = useState<Quote[]>([])
  const [selectedQuote, setSelectedQuote] = useState<Quote | null>(null)
  const [loading, setLoading] = useState(true)
  const [newLine, setNewLine] = useState<QuoteLine>({
    label: '',
    quantity: 1,
    unit_price: 0,
    total: 0,
  })

  useEffect(() => {
    fetchQuotes()
  }, [])

  useEffect(() => {
    if (newLine.quantity && newLine.unit_price) {
      setNewLine({
        ...newLine,
        total: newLine.quantity * newLine.unit_price,
      })
    }
  }, [newLine.quantity, newLine.unit_price])

  const fetchQuotes = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${API_URL}/api/quotes`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      if (response.ok) {
        const data = await response.json()
        setQuotes(data)
      }
    } catch (error) {
      console.error('Error fetching quotes:', error)
    } finally {
      setLoading(false)
    }
  }

  const addLine = async () => {
    if (!selectedQuote || !newLine.label) return

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(
        `${API_URL}/api/quotes/${selectedQuote.id}/lines`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify(newLine),
        }
      )
      if (response.ok) {
        setNewLine({ label: '', quantity: 1, unit_price: 0, total: 0 })
        fetchQuotes()
      }
    } catch (error) {
      console.error('Error adding line:', error)
    }
  }

  const generatePDF = async (quoteId: string) => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(
        `${API_URL}/api/quotes/${quoteId}/pdf`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      )
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `devis-${quoteId}.pdf`
        a.click()
      }
    } catch (error) {
      console.error('Error generating PDF:', error)
    }
  }

  const createNewVersion = async (quoteId: string) => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(
        `${API_URL}/api/quotes/${quoteId}/versions`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      )
      if (response.ok) {
        fetchQuotes()
      }
    } catch (error) {
      console.error('Error creating version:', error)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft':
        return 'secondary'
      case 'sent':
        return 'default'
      case 'accepted':
        return 'outline'
      case 'rejected':
        return 'destructive'
      default:
        return 'secondary'
    }
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'draft':
        return 'Brouillon'
      case 'sent':
        return 'Envoyé'
      case 'accepted':
        return 'Accepté'
      case 'rejected':
        return 'Refusé'
      default:
        return status
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-muted-foreground">Chargement...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Devis</h1>
        <p className="text-muted-foreground">
          Créez et gérez vos devis avec versioning
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Liste des devis</CardTitle>
            <CardDescription>
              Sélectionnez un devis pour le modifier
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {quotes.map((quote) => (
                <div
                  key={quote.id}
                  className={`p-4 border rounded-lg cursor-pointer hover:bg-muted transition-colors ${
                    selectedQuote?.id === quote.id ? 'border-primary bg-muted' : ''
                  }`}
                  onClick={() => setSelectedQuote(quote)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="font-medium">Devis #{quote.id.slice(0, 8)}</div>
                    <Badge variant={getStatusColor(quote.status)}>
                      {getStatusLabel(quote.status)}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between text-sm text-muted-foreground">
                    <span>Version {quote.current_version}</span>
                    <span className="font-medium">{quote.total.toFixed(2)} €</span>
                  </div>
                </div>
              ))}
            </div>
            {quotes.length === 0 && (
              <div className="text-center py-8 text-muted-foreground">
                Aucun devis. Les devis sont créés automatiquement à l'ouverture d'un chantier.
              </div>
            )}
          </CardContent>
        </Card>

        {selectedQuote && (
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Devis #{selectedQuote.id.slice(0, 8)}</CardTitle>
                  <CardDescription>
                    Version {selectedQuote.current_version}
                  </CardDescription>
                </div>
                <div className="flex gap-2">
                  <Button size="sm" variant="outline" onClick={() => generatePDF(selectedQuote.id)}>
                    PDF
                  </Button>
                  <Button size="sm" onClick={() => createNewVersion(selectedQuote.id)}>
                    Nouvelle version
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <Label>Lignes du devis</Label>
                <div className="space-y-2">
                  {selectedQuote.lines?.map((line, index) => (
                    <div key={index} className="p-3 border rounded-lg">
                      <div className="font-medium">{line.label}</div>
                      <div className="flex justify-between text-sm text-muted-foreground mt-1">
                        <span>
                          {line.quantity} × {line.unit_price.toFixed(2)} €
                        </span>
                        <span className="font-medium">{line.total.toFixed(2)} €</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="border-t pt-4 space-y-3">
                <Label>Ajouter une ligne</Label>
                <div className="space-y-2">
                  <Textarea
                    placeholder="Description de la prestation"
                    value={newLine.label}
                    onChange={(e) => setNewLine({ ...newLine, label: e.target.value })}
                  />
                  <div className="grid grid-cols-3 gap-2">
                    <Input
                      type="number"
                      placeholder="Quantité"
                      value={newLine.quantity}
                      onChange={(e) =>
                        setNewLine({ ...newLine, quantity: parseFloat(e.target.value) || 0 })
                      }
                    />
                    <Input
                      type="number"
                      placeholder="Prix unitaire"
                      value={newLine.unit_price}
                      onChange={(e) =>
                        setNewLine({ ...newLine, unit_price: parseFloat(e.target.value) || 0 })
                      }
                    />
                    <Input
                      type="number"
                      placeholder="Total"
                      value={newLine.total.toFixed(2)}
                      disabled
                    />
                  </div>
                  <Button onClick={addLine} className="w-full">
                    Ajouter
                  </Button>
                </div>
              </div>

              <div className="border-t pt-4">
                <div className="flex justify-between items-center text-lg font-bold">
                  <span>Total HT</span>
                  <span>{selectedQuote.total.toFixed(2)} €</span>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
