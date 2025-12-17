import { Link, useLocation } from 'react-router-dom'
import { Button } from './ui/button'

interface SidebarProps {
  onLogout: () => void
}

export default function Sidebar({ onLogout }: SidebarProps) {
  const location = useLocation()

  const isActive = (path: string) => location.pathname === path

  const menuItems = [
    { path: '/', label: 'Tableau de bord', icon: '📊' },
    { path: '/projects', label: 'Chantiers', icon: '🏗️' },
    { path: '/customers', label: 'Clients', icon: '👥' },
    { path: '/metrage', label: 'Métrage', icon: '📐' },
    { path: '/quotes', label: 'Devis', icon: '📄' },
  ]

  return (
    <aside className="w-64 h-screen flex flex-col border-r bg-card">
      <div className="h-16 border-b flex items-center px-6">
        <h1 className="text-xl font-bold text-primary">Facade Suite</h1>
      </div>

      <nav className="flex-1 overflow-y-auto p-4">
        <div className="space-y-2">
          {menuItems.map((item) => (
            <Link key={item.path} to={item.path}>
              <Button
                variant={isActive(item.path) ? 'default' : 'ghost'}
                className="w-full justify-start"
              >
                <span className="mr-2">{item.icon}</span>
                {item.label}
              </Button>
            </Link>
          ))}
        </div>
      </nav>

      <div className="p-4 border-t">
        <div className="space-y-2">
          <div className="text-sm text-muted-foreground px-2">
            <div className="font-medium">SARL Plein Sud Crépis</div>
            <div className="text-xs">Plan TRIAL (14 jours)</div>
          </div>
          <Button variant="outline" className="w-full" onClick={onLogout}>
            Se déconnecter
          </Button>
        </div>
      </div>
    </aside>
  )
}
