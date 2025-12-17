import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import { Badge } from '../components/ui/badge'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../components/ui/dialog'
import { API_URL } from '../config'

interface Customer {
  id: string
  name: string
  email: string
  phone: string
  city: string
}

interface Project {
  id: string
  name: string
  status: string
  customer_id: string
  customer?: Customer
  created_at: string
}

export default function Projects() {
  const [projects, setProjects] = useState<Project[]>([])
  const [customers, setCustomers] = useState<Customer[]>([])
  const [loading, setLoading] = useState(true)
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [newProject, setNewProject] = useState({
    name: '',
    customer_id: '',
  })

  useEffect(() => {
    fetchProjects()
    fetchCustomers()
  }, [])

  const fetchProjects = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${API_URL}/api/projects`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      if (response.ok) {
        const data = await response.json()
        setProjects(data)
      }
    } catch (error) {
      console.error('Error fetching projects:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchCustomers = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${API_URL}/api/customers`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      if (response.ok) {
        const data = await response.json()
        setCustomers(data)
      }
    } catch (error) {
      console.error('Error fetching customers:', error)
    }
  }

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${API_URL}/api/projects`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(newProject),
      })
      if (response.ok) {
        setIsCreateOpen(false)
        setNewProject({ name: '', customer_id: '' })
        fetchProjects()
      }
    } catch (error) {
      console.error('Error creating project:', error)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft':
        return 'secondary'
      case 'in_progress':
        return 'default'
      case 'completed':
        return 'outline'
      default:
        return 'secondary'
    }
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'draft':
        return 'Brouillon'
      case 'in_progress':
        return 'En cours'
      case 'completed':
        return 'Terminé'
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Chantiers</h1>
          <p className="text-muted-foreground">
            Gérez vos chantiers de façade
          </p>
        </div>
        <Button onClick={() => setIsCreateOpen(true)}>
          Nouveau chantier
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {projects.map((project) => (
          <Card key={project.id} className="cursor-pointer hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-xl">{project.name}</CardTitle>
                <Badge variant={getStatusColor(project.status)}>
                  {getStatusLabel(project.status)}
                </Badge>
              </div>
              <CardDescription>
                {project.customer?.name || 'Client non défini'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                {project.customer?.city && (
                  <div className="text-muted-foreground">
                    📍 {project.customer.city}
                  </div>
                )}
                <div className="text-muted-foreground">
                  Créé le {new Date(project.created_at).toLocaleDateString('fr-FR')}
                </div>
              </div>
              <div className="mt-4 flex gap-2">
                <Button size="sm" variant="outline" className="flex-1">
                  Métrage
                </Button>
                <Button size="sm" variant="outline" className="flex-1">
                  Devis
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {projects.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <div className="text-center space-y-2">
              <h3 className="text-lg font-semibold">Aucun chantier</h3>
              <p className="text-muted-foreground">
                Commencez par créer votre premier chantier
              </p>
              <Button onClick={() => setIsCreateOpen(true)} className="mt-4">
                Créer un chantier
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Nouveau chantier</DialogTitle>
            <DialogDescription>
              Créez un nouveau chantier pour un client
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleCreateProject} className="space-y-4 mt-4">
            <div className="space-y-2">
              <Label htmlFor="name">Nom du chantier</Label>
              <Input
                id="name"
                value={newProject.name}
                onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                placeholder="Ex: Rénovation façade principale"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="customer">Client</Label>
              <select
                id="customer"
                value={newProject.customer_id}
                onChange={(e) => setNewProject({ ...newProject, customer_id: e.target.value })}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                required
              >
                <option value="">Sélectionner un client</option>
                {customers.map((customer) => (
                  <option key={customer.id} value={customer.id}>
                    {customer.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex gap-2 justify-end">
              <Button type="button" variant="outline" onClick={() => setIsCreateOpen(false)}>
                Annuler
              </Button>
              <Button type="submit">
                Créer
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  )
}
