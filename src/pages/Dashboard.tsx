import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Link } from 'react-router-dom'
import { API_URL } from '../config'

interface Stats {
  projects: number
  customers: number
  quotes: number
  revenue: number
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats>({
    projects: 0,
    customers: 0,
    quotes: 0,
    revenue: 0,
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${API_URL}/api/stats`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (error) {
      console.error('Error fetching stats:', error)
    } finally {
      setLoading(false)
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
        <h1 className="text-3xl font-bold">Tableau de bord</h1>
        <p className="text-muted-foreground">
          Vue d'ensemble de votre activité
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Chantiers actifs</CardTitle>
            <span className="text-2xl">🏗️</span>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.projects}</div>
            <p className="text-xs text-muted-foreground">
              en cours ou terminés
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Clients</CardTitle>
            <span className="text-2xl">👥</span>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.customers}</div>
            <p className="text-xs text-muted-foreground">
              dans votre base
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Devis</CardTitle>
            <span className="text-2xl">📄</span>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.quotes}</div>
            <p className="text-xs text-muted-foreground">
              créés ce mois
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Chiffre d'affaires</CardTitle>
            <span className="text-2xl">💰</span>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.revenue.toFixed(2)} €</div>
            <p className="text-xs text-muted-foreground">
              devis acceptés
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Actions rapides</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Link to="/projects">
              <Button className="w-full justify-start" variant="outline">
                🏗️ Nouveau chantier
              </Button>
            </Link>
            <Link to="/customers">
              <Button className="w-full justify-start" variant="outline">
                👥 Ajouter un client
              </Button>
            </Link>
            <Link to="/metrage">
              <Button className="w-full justify-start" variant="outline">
                📐 Métrage photo
              </Button>
            </Link>
            <Link to="/quotes">
              <Button className="w-full justify-start" variant="outline">
                📄 Créer un devis
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Support & Aide</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="text-sm space-y-2">
              <p className="text-muted-foreground">
                Besoin d'aide ? Contactez notre support :
              </p>
              <div className="flex items-center gap-2">
                <span>✉️</span>
                <a href="mailto:gsmfarid@hotmail.fr" className="text-primary hover:underline">
                  gsmfarid@hotmail.fr
                </a>
              </div>
            </div>
            <Button variant="outline" className="w-full">
              Signaler un problème
            </Button>
          </CardContent>
        </Card>
      </div>

      <Card className="bg-blue-50 border-blue-200">
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <div className="text-2xl">ℹ️</div>
            <div className="space-y-1">
              <p className="font-medium text-blue-900">Note juridique importante</p>
              <p className="text-sm text-blue-800">
                Facade Suite est un outil d'aide au métrage. Vous restez seul responsable 
                de la vérification finale des métrés. L'éditeur ne peut être tenu responsable 
                des erreurs de mesure.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
